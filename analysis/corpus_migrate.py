#!/usr/bin/env python3
"""Reconstruct the observation log from git history, so the store does not start empty.

Every commit that touched data/posts is an observation checkpoint: an item first appearing in
commit N was first seen somewhere between commit N-1 and commit N. Walking the 11 corpus commits
in order and ingesting each tree as a snapshot recovers first_seen_at for the whole corpus to
within one pull -- which is exactly the resolution the feed_lag instrument was reconstructing by
hand, one issue at a time.

OBSERVATION TIME. A commit's timestamp is when the issue was written up, not when the corpus was
read; the weather results.json for that issue records the actual `pull_at`, which is up to several
hours earlier and is the honest observation time. We use pull_at where the issue published one and
fall back to the commit time where it did not (issues #1-#2, and the initial corpus commit).

WHAT THIS CAN AND CANNOT RECOVER. Items are dated by the pull that first contained them, so
first_seen_at is accurate to one pull interval, not to the second. An item created and edited
between two consecutive pulls shows only its later version -- the intermediate version was never
observed and honestly should not appear. Nothing here invents observations.

Usage: python3 analysis/corpus_migrate.py [--dry-run]
"""
import argparse, json, subprocess, sys, tarfile, tempfile, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS
from weather_cutoff_margin import _parse_stamp

REPO = Path(__file__).resolve().parent.parent


def corpus_commits():
    """-> [(sha, commit_epoch, subject)] oldest first, for every commit touching data/posts."""
    out = subprocess.run(["git", "log", "--reverse", "--format=%H\t%ct\t%s", "--", "data/posts"],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    rows = []
    for line in out.splitlines():
        h, ct, subj = line.split("\t", 2)
        rows.append((h, float(ct), subj))
    return rows


def observed_at_for(sha, commit_epoch):
    """The pull time this commit's corpus was read at, falling back to the commit time."""
    show = subprocess.run(["git", "show", f"{sha}:results/weather"], cwd=REPO,
                          capture_output=True, text=True)
    if show.returncode == 0:
        # newest issue directory present in this commit
        dirs = sorted(l.strip().rstrip("/") for l in show.stdout.splitlines()
                      if l.strip().startswith("20"))
        for d in reversed(dirs):
            r = subprocess.run(["git", "show", f"{sha}:results/weather/{d}/results.json"],
                               cwd=REPO, capture_output=True, text=True)
            if r.returncode != 0:
                continue
            try:
                pull = json.loads(r.stdout).get("pull_at")
            except Exception:
                continue
            ts = _parse_stamp(pull)
            if ts:
                return ts, f"pull_at of {d}"
    return commit_epoch, "commit time (no published pull_at)"


def snapshot_items(sha):
    """-> {item_key: row} for data/posts at a commit, without touching the working tree."""
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run(["git", "archive", sha, "data/posts"], cwd=REPO,
                              capture_output=True, check=True)
        with tarfile.open(fileobj=__import__("io").BytesIO(proc.stdout)) as tf:
            tf.extractall(td)
        items, threads = CS.scan_tree(Path(td) / "data" / "posts")
    return items, threads


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if CS.OBS_LOG.exists() and not args.dry_run:
        sys.exit(f"{CS.OBS_LOG} already exists; delete it to rebuild from scratch")

    known, total_new, total_edit = {}, 0, 0
    print(f"{'commit':9s} {'observed_at':20s} {'items':>7s} {'new':>7s} {'edits':>6s}  source")
    for sha, ct, subj in corpus_commits():
        obs_at, src = observed_at_for(sha, ct)
        items, _threads = snapshot_items(sha)
        if args.dry_run:
            new = sum(1 for k, r in items.items() if known.get(k) != r["content_sha"]
                      and k not in known)
            edit = sum(1 for k, r in items.items() if k in known
                       and known[k] != r["content_sha"])
            for k, r in items.items():
                known[k] = r["content_sha"]
        else:
            rid = f"git:{sha[:8]}"
            new, edit = CS.append_snapshot(items, obs_at, run_id=rid, known=known)
            # every historical pull was a full re-read of every thread, so it is a complete run
            CS.append_run({"run_id": rid, "started_at": obs_at, "ended_at": obs_at, "mode": "full",
                           "cursor_before": None, "cursor_after": None,
                           "threads_attempted": len(_threads), "threads_ok": len(_threads),
                           "threads_404": 0, "threads_429": 0, "complete": 1,
                           "note": f"reconstructed from commit {sha[:8]}: {subj[:60]}"})
        total_new += new; total_edit += edit
        stamp = time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(obs_at))
        print(f"{sha[:8]:9s} {stamp:20s} {len(items):>7d} {new:>7d} {edit:>6d}  {src}")

    print(f"\n{total_new} item-versions first seen, {total_edit} edits recorded"
          + ("  [dry run, nothing written]" if args.dry_run else f" -> {CS.OBS_LOG}"))
