#!/usr/bin/env python3
"""Weather report — CPU half. Hard cutoff from $WEATHER_CUTOFF (YYYY-MM-DD = that date's
midnight UTC, exclusive): items with t >= cutoff are excluded everywhere. Issue window =
(last item of the previous issue's corpus, cutoff). Instruments: inflows, cohort survival,
calendar-day churn, activity-clock churn signatures (7 equal item-count windows, core = active
in >=3 windows) for agent AND anchors, raw-zstd register, feed lag (backfill + post-publication
content mutations). Outputs weather_cpu_out.json."""
import json, sys, hashlib, datetime as dt
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import sys; sys.path.insert(0, '/home/dan/personal/memetic/analysis')
from weather_churn import signature_windows   # single source of truth; see weather_churn_control.py

import os
S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
_c = os.environ["WEATHER_CUTOFF"]  # e.g. "2026-08-14" = midnight UTC upper bound (exclusive)
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import zstd_curve as Z

CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()

def load_items(d, cutoff=CUTOFF):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20 and t < cutoff]

PREV = load_items(S / "prev_corpus/data/posts")          # issue-1 corpus state (git HEAD)
NEW = load_items("/home/dan/personal/memetic/data/posts")
prev_last = max(t for t, _, _, _ in PREV)
print(f"prev-issue items {len(PREV)} (last {dt.datetime.utcfromtimestamp(prev_last):%m-%d %H:%M}), "
      f"this-issue items {len(NEW)} (cutoff {_c} 00:00 UTC)", flush=True)

day = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
days = sorted({day(t) for t, _, _, _ in NEW})

# --- feed-lag / backfill instrument: items that existed-in-time at the previous pull but were
# invisible to it (timestamp <= prev pull's last item, absent from prev_corpus). Quantifies the
# undercount of trailing-day numbers so the newest day is reported as provisional. ---
prev_keys = {k for _, k, _, _ in PREV}
backfill = [(t, k, a) for t, k, x, a in NEW if k not in prev_keys and t <= prev_last]
bf_day = {}
for t, k, a in backfill: bf_day[day(t)] = bf_day.get(day(t), 0) + 1
prev_first = {}
for t, k, x, a in PREV:
    if a not in prev_first: prev_first[a] = t
bf_authors = {a for t, k, a in backfill if a not in prev_first}
lags_h = sorted((prev_last - t) / 3600 for t, k, a in backfill)
feed_lag = {"backfilled_items": len(backfill), "by_day": bf_day,
            "new_authors_revealed": len(bf_authors),
            "item_age_at_missed_pull_hours": {"median": round(lags_h[len(lags_h)//2], 2) if lags_h else None,
                                              "p90": round(lags_h[int(len(lags_h)*0.9)], 2) if lags_h else None},
            "note": "trailing-day counts are provisional: this pull's view of its final hours will be revised upward by roughly this issue's backfill rate"}

# --- content-mutation check (issue-3 watch item #4): items present in BOTH corpora under the
# same id whose TEXT changed after publication. id-keyed caches (claims, allocation labels)
# cannot see this and retain stale values until the item is re-processed; observed moving
# frozen-day register cells at the 4th decimal between issues. ---
_h = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
prev_text = {k: x for _, k, x, _ in PREV}
edited = [(t, k, a) for t, k, x, a in NEW if k in prev_text and _h(x) != _h(prev_text[k])]
ed_day = Counter(day(t) for t, k, a in edited)
delta_chars = [len(x) - len(prev_text[k]) for _, k, x, _ in NEW if k in prev_text and _h(x) != _h(prev_text[k])]
feed_lag["content_mutations"] = {
    "items_compared": len(prev_text),
    "edited_items": len(edited),
    "by_day": dict(sorted(ed_day.items())),
    "authors_affected": len({a for _, _, a in edited}),
    "char_delta": {"median": float(np.median(delta_chars)) if delta_chars else None,
                   "min": min(delta_chars) if delta_chars else None,
                   "max": max(delta_chars) if delta_chars else None},
    "edited_keys": [f"{k[0]}:{k[1]}" for _, k, _ in edited],
    "note": "post-publication text edits; invisible to id-keyed claim/allocation caches. weather_gpu.py evicts these keys and re-processes them."}

out = {"cutoff_utc": _c + "T00:00:00Z", "issue_window_start_utc":
       dt.datetime.utcfromtimestamp(prev_last).strftime("%Y-%m-%d %H:%M"),
       "corpus": {"items": len(NEW), "posts": sum(1 for _, k, _, _ in NEW if k[0] == "post"),
                  "authors": len({a for _, _, _, a in NEW}), "days": days,
                  "issue_window_items": sum(1 for t, _, _, _ in NEW if t > prev_last)}}

first_seen, per_day_new, per_day_items, newcomer_items = {}, Counter(), Counter(), Counter()
per_day_active = defaultdict(set)
for t, k, x, a in NEW:
    d = day(t)
    per_day_items[d] += 1; per_day_active[d].add(a)
    if a not in first_seen: first_seen[a] = d; per_day_new[d] += 1
    if first_seen[a] == d: newcomer_items[d] += 1
out["inflows"] = {d: {"new_authors": per_day_new[d], "active_authors": len(per_day_active[d]),
                      "items": per_day_items[d],
                      "newcomer_item_share": round(newcomer_items[d] / per_day_items[d], 3)} for d in days}

by_author_days = defaultdict(set)
for t, k, x, a in NEW: by_author_days[a].add(day(t))
coh = {}
for d in days:
    members = [a for a, fd in first_seen.items() if fd == d]
    if not members: continue
    coh[d] = {"n": len(members),
              "survival": {dd: round(sum(1 for a in members if dd in by_author_days[a]) / len(members), 3)
                           for dd in days if dd > d},
              "median_active_days": float(np.median([len(by_author_days[a]) for a in members]))}
out["cohort_survival"] = coh

out["churn_signature_day_K3"] = signature_windows([(day(t), a) for t, k, x, a in NEW])
out["churn_signature_day_K3"]["note"] = "calendar-day windows; series-internal comparison only"

# NEW: activity-clock signatures — 7 equal item-count windows over each corpus's FIRST n_agent items
def anchor_events(fam, src):
    C = json.load(open(S / src))[fam]
    return sorted((r["ts"], r["author"]) for r in C if len(r["text"]) >= 20)
n_agent = len(NEW)
act_sigs = {"agent": signature_windows([(min(6, i * 7 // n_agent), a) for i, (t, k, x, a) in enumerate(NEW)])}
for fam, src in [("lisp", "baseline_corpora.json"), ("sci", "baseline_corpora.json"),
                 ("forth", "baseline_corpora2.json"), ("smalltalk", "baseline_corpora2.json"),
                 ("scheme", "baseline_corpora2.json")]:
    ev = anchor_events(fam, src)[:n_agent]
    n = len(ev)
    act_sigs[fam] = signature_windows([(min(6, i * 7 // n), a) for i, (t, a) in enumerate(ev)]) | \
                    {"n_items": n, "span_days": round((ev[-1][0] - ev[0][0]) / 86400, 0)}
out["activity_clock_signatures"] = {"design": "each corpus's first min(N, n_agent) items split into 7 equal item-count windows; core = active in >=3 windows; clock-free, commensurable by construction",
                                    "signatures": act_sigs}

# register trend
class Args: level = 19; window_bytes = 524288; bucket = 25; seed = 42
mk = [{"kind": k[0], "id": k[1], "post_id": 0, "created_at": t, "author": a, "author_model": "", "text": x}
      for t, k, x, a in NEW]
rows = Z.compute_metrics(mk, Args())
agg = lambda rs: sum(r["cond_win_bits"] for r in rs) / sum(r["self_bits"] for r in rs)
per_day_z = {d: round(agg([r for r in rows if day(r["created_at"]) == d]), 4)
             for d in days if sum(1 for r in rows if day(r["created_at"]) == d) >= 50}
out["zstd_raw"] = {"whole": round(agg(rows), 4), "per_day": per_day_z, "band_floor": 0.704}
out["feed_lag"] = feed_lag
json.dump(out, open(S / "weather_cpu_out.json", "w"), indent=1)
print("day churn:", out["churn_signature_day_K3"], flush=True)
print("activity-clock:", {k: {kk: v[kk] for kk in ("core_dominance_pct", "stability_ratio", "permeability_pct")}
                          for k, v in act_sigs.items()}, flush=True)
print("inflows:", {d: v["new_authors"] for d, v in out["inflows"].items()}, flush=True)
print("zstd:", per_day_z, flush=True)
print("feed_lag: backfill", feed_lag["backfilled_items"], "| edited items",
      feed_lag["content_mutations"]["edited_items"], feed_lag["content_mutations"]["by_day"], flush=True)
print("saved weather_cpu_out.json")
