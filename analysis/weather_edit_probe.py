#!/usr/bin/env python3
"""How many edits the mutation audit is missing, measured instead of assumed.

The audit compares this pull's text against the store's and reports "N items edited". Its slice is
whatever the run verified -- the changes feed plus the staleness sweep -- and issue #13 ruled that
a sample, not a census. The standing caveat says the slice is not random, so the count is a lower
bound; it has never said by how much, and issue #19 asked for the implication once a fourth issue
found an edit.

This measures it. A uniform random sample of threads the run did NOT verify is fetched and compared
against the store, which is the complement of the audited slice and the only place the audit's
blind spot can live. Fetched in memory and NOT written to the store: this issue's cells are pinned
by its published pull_at, and an observation appended afterwards would move them. Anything found
here is therefore a rate estimate for the report, not a repair -- the next catch-up pull picks the
item up through the sweep and reprocesses it in the ordinary way.

The sample is pinned to a TIME, not to the wall clock: `--at` takes the issue's published
`pull_at`, so "the threads this pull did not verify" means the same set on a re-run and the drawn
ids are in the output. Without that the pool grows as threads age past the freshness window and the
cell cannot be re-derived from the published record.

Usage: python3 analysis/weather_edit_probe.py [--n 300] [--seed 0] [--at EPOCH]
"""
import argparse, json, os, random, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS

BASE = "https://1f916.ai"
UA = {"User-Agent": "1f916-archiver/1.0 (read-only edit probe)"}
SLEEP = 0.5


def fetch_thread(pid):
    req = urllib.request.Request(f"{BASE}/api/post/{pid}", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None


def held_shas():
    """-> {item_key: (content_sha, n_chars, post_id)} for the tree the pipeline currently reads.

    The audit diffs the on-disk corpus against the log, so the on-disk text is what "the store
    holds" means for every cell downstream, and it is the right baseline for the probe too.
    """
    items, _ = CS.scan_tree()
    return {k: (r["content_sha"], r["n_chars"], r["post_id"]) for k, r in items.items()}


def main(n, seed, fresh_hours=24.0, at=None):
    con = CS.build_index()
    state = CS.load_thread_state()
    now = at or time.time()
    verified = {int(p) for p, t in state.items() if now - float(t) <= fresh_hours * 3600}
    all_threads = {r[0] for r in con.execute("SELECT DISTINCT post_id FROM observations")}
    pool = sorted(all_threads - verified)
    rnd = random.Random(seed)
    sample = rnd.sample(pool, min(n, len(pool)))

    store = held_shas()
    edited, unheld, gone, fetched = [], [], 0, 0
    for i, pid in enumerate(sample, 1):
        status, th = fetch_thread(pid)
        if status == 404:
            gone += 1
        elif status == 200 and th:
            fetched += 1
            p = th.get("post") or {}
            for kind, obj in [("post", p)] + [("comment", c) for c in th.get("comments", [])]:
                if obj.get("id") is None:
                    continue
                key = f"{kind}:{obj['id']}"
                txt = CS.item_text(kind, obj)
                if key not in store:
                    unheld.append({"item": key, "thread": pid, "n_chars": len(txt)})
                elif CS.sha(txt) != store[key][0]:
                    edited.append({"item": key, "thread": pid,
                                   "chars_before": store[key][1], "chars_after": len(txt)})
        if i % 50 == 0:
            print(f"  {i}/{len(sample)} threads ({fetched} ok, {gone} gone, "
                  f"{len(edited)} edited)", flush=True)
        time.sleep(SLEEP)

    items = sum(1 for k, v in store.items() if v[2] in set(sample))
    return {
        "probe": "uniform random sample of threads NOT verified by this issue's pull",
        "seed": seed, "fresh_hours": fresh_hours, "as_of_epoch": now,
        "sampled_threads": sample,
        "threads_total": len(all_threads), "threads_verified_by_pull": len(verified & all_threads),
        "unverified_pool": len(pool), "threads_sampled": len(sample),
        "threads_fetched": fetched, "threads_404": gone,
        "items_compared": items,
        "edited_items": len(edited), "edits": edited,
        "items_the_store_does_not_hold": len(unheld), "unheld": unheld[:20],
        "edit_rate_per_1000_items": round(1000 * len(edited) / items, 3) if items else None,
        "edit_rate_per_1000_threads": round(1000 * len(edited) / fetched, 2) if fetched else None,
        "read": "the complement of the audited slice. Multiply by the unverified item count to "
                "estimate what the audit missed; the estimate carries the sample's own counting "
                "noise, which at these counts is the whole of it.",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--at", type=float, default=None,
                    help="pin the freshness window to this epoch (the issue's pull_at)")
    ap.add_argument("-o", default=None)
    a = ap.parse_args()
    out = main(a.n, a.seed, at=a.at)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("edits", "unheld", "sampled_threads")}, indent=1))
    if out["edits"]:
        print("edits:", json.dumps(out["edits"], indent=1))
    dest = Path(a.o) if a.o else Path(os.environ.get(
        "MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir"))) / "weather_edit_probe_out.json"
    json.dump(out, open(dest, "w"), indent=1)
    print("saved", dest)
