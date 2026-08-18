#!/usr/bin/env python3
"""Window-matched early-retention: the achievable fragment of cohort survival.
Full survival curves are impossible here (1f916 is 3 days old; human forums span
years; agent 'churn' is operator scheduling, not engagement). But we CAN censor
every author to a fixed window from their FIRST post and ask: did they come back?

For each author with a full W-hour observation window (first post <= corpus_end - W),
count distinct SESSION buckets (6h) with activity inside [first, first+W]. 'Returned'
= active in >= 2 sessions (came back in a later block, not just a thread burst).

Valid only where per-author capture is COMPLETE (a full pull or a near-complete
scrape); a thin thread sample undercounts return and must be marked incomplete.
CPU-only."""
import json, statistics as st, sys
from collections import defaultdict
from pathlib import Path

# Usage: retention.py "<label>=<data-dir>[=complete]" ...  (complete=1 if per-author capture is
# complete; a thin sample undercounts return and should be marked incomplete).
if len(sys.argv) < 2:
    sys.exit('usage: retention.py "label=data_dir[=complete]" ...')
CORPORA = []
for _a in sys.argv[1:]:
    _p = _a.split("=")
    CORPORA.append((_p[0], _p[1], len(_p) > 2 and _p[2] in ("1", "true", "True")))
H = 3600_000
SESSION_H = 6


def author_times(data_dir):
    at = defaultdict(list)
    spec = str(data_dir)
    if ":" in spec and spec.rsplit(":", 1)[0].endswith(".json"):
        # canonical anchor corpus: "<corpora.json>:<family>"; ts stored in SECONDS
        path, fam = spec.rsplit(":", 1)
        for r in json.load(open(path))[fam]:
            at[r["author"]].append(int(r["ts"]) * 1000)
        return {a: sorted(ts) for a, ts in at.items()}
    for f in Path(data_dir).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        at[p["author"]].append(p["created_at"])
        for c in th.get("comments", []):
            at[c["author"]].append(c["created_at"])
    return {a: sorted(ts) for a, ts in at.items()}


def _exists(spec):
    spec = str(spec)
    if ":" in spec and spec.rsplit(":", 1)[0].endswith(".json"):
        return Path(spec.rsplit(":", 1)[0]).exists()
    return Path(spec).exists()


def retention(at, W_hours):
    W = W_hours * H
    end = max(t for ts in at.values() for t in ts)
    rows = []
    for a, ts in at.items():
        if ts[0] > end - W:               # not enough observation window -> censor
            continue
        first = ts[0]
        win = [t for t in ts if first <= t < first + W]
        sessions = len({int((t - first) // (SESSION_H * H)) for t in win})
        rows.append((sessions, len(win)))
    if not rows:
        return None
    n = len(rows)
    return {"n_qualifying": n, "n_total_authors": len(at),
            "return_rate": round(sum(s >= 2 for s, _ in rows) / n, 3),
            "one_and_done_rate": round(sum(i == 1 for _, i in rows) / n, 3),
            "median_sessions": st.median(s for s, _ in rows),
            "median_items": st.median(i for _, i in rows),
            "mean_items": round(st.mean(i for _, i in rows), 1)}


for label, d, complete in CORPORA:
    if not _exists(d):
        print(f"{label}: missing"); continue
    at = author_times(d)
    print(f"\n=== {label} {'' if complete else '[incomplete capture — return undercounted]'} ===")
    for W in (12, 24, 48):
        r = retention(at, W)
        if r:
            print(f"  W={W}h: return_rate {r['return_rate']:.0%}  one&done {r['one_and_done_rate']:.0%}  "
                  f"med_items {r['median_items']}  med_sessions {r['median_sessions']}  "
                  f"(n_qual {r['n_qualifying']}/{r['n_total_authors']})")
