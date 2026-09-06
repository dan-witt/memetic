#!/usr/bin/env python3
"""The per-post vote panel, recovered from the git history of data/posts/.

WHY THIS EXISTS. The observation store records what we observed and when, but it has no votes
column -- observations.jsonl carries n_chars and content_sha, not scores. Votes therefore have
exactly one history in this repo: data/posts/ is tracked, so every commit that touched it is a
wave of vote readings. 22 waves, 2026-08-08 to 2026-09-02.

DATING A READING. Not by commit date. corpus_fetch.py runs a staleness sweep, so a commit carries
readings for threads it did not refetch that day -- the median post has only 2 distinct fetch
times ever, and the newest reading in the tree is a median 7.6 days old. thread_state.json is
tracked too and maps post_id -> last_fetched_at, so each reading is dated by when that thread was
actually pulled. Before the store existed (waves 0-10, through 2026-08-22) there is no such map
and the commit time is the only date available; those rows are marked dated_by="commit".

Usage:  python3 premium/panel.py vote_panel.json
"""
import json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def sh(*a):
    return subprocess.run(a, cwd=REPO, capture_output=True, check=True).stdout


def build(log=sys.stderr):
    commits = [c.split() for c in sh("git", "log", "--format=%h %ct", "--",
                                     "data/posts/").decode().split("\n") if c.strip()][::-1]
    print(f"{len(commits)} waves", file=log)
    panel = {}
    for wave, (sha, ctime) in enumerate(commits):
        ctime = float(ctime)
        try:
            ts = {int(k): float(v) for k, v in
                  json.loads(sh("git", "show", f"{sha}:data/thread_state.json")).items()}
        except subprocess.CalledProcessError:
            ts = {}                                  # pre-store waves: commit time is all there is
        blobs, ids = [], []
        for ent in sh("git", "ls-tree", "-r", "-z", sha, "data/posts/").decode().split("\0"):
            if not ent.strip():
                continue
            meta, path = ent.split("\t", 1)
            blobs.append(meta.split()[2]); ids.append(int(Path(path).stem))
        # one batch call: 3,646 separate `git show`es per wave is minutes, this is seconds
        p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=REPO,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, _ = p.communicate(("\n".join(blobs) + "\n").encode())
        pos = 0
        for pid in ids:
            nl = out.index(b"\n", pos)
            size = int(out[pos:nl].split()[2])
            body = out[nl + 1:nl + 1 + size]
            pos = nl + 1 + size + 1
            try:
                post = json.loads(body)["post"]
            except Exception:
                continue
            cat = post.get("created_at") or 0
            panel.setdefault(pid, []).append({
                "wave": wave, "sha": sha,
                "read_at": ts.get(pid, ctime),
                "dated_by": "fetch" if pid in ts else "commit",
                "votes": post.get("votes", 0),
                "created_at": cat / 1000 if cat > 1e12 else float(cat),
                "author": post.get("author"), "author_model": post.get("author_model"),
                "title": post.get("title"),
                "n_chars": len(((post.get("title") or "") + "\n\n"
                                + (post.get("body") or "")).strip()),
                "mod_state": post.get("mod_state"),
            })
        print(f"  wave {wave:>2} {sha} {len(ids):>5} posts, {len(ts):>5} fetch-times", file=log)
    return panel


def latest(rows):
    return sorted(rows, key=lambda r: r["read_at"])[-1]


def settled(panel, min_age_h=48):
    """Post ids whose newest reading was taken at least min_age_h after the post was created.

    Votes stop accruing after ~2 days (see the `accrual` stage), so a settled reading is a final
    score even when it is a week stale. The unsettled remainder is young, not neglected.
    """
    return [pid for pid, rows in panel.items()
            if (latest(rows)["read_at"] - latest(rows)["created_at"]) >= min_age_h * 3600]


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "vote_panel.json")
    p = build()
    json.dump(p, open(out, "w"))
    print(f"wrote {out}: {len(p)} posts, {len(settled(p))} settled", file=sys.stderr)
