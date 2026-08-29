#!/usr/bin/env python3
"""Weather report — CPU half. Hard cutoff from $WEATHER_CUTOFF (YYYY-MM-DD = that date's
midnight UTC, exclusive): items with t >= cutoff are excluded everywhere. Issue window =
[previous published issue's CUTOFF, this cutoff) -- the basis adopted at issue #9; issues #1-#8
started it at the previous PULL's last item, which is retired. weather_issue_boundary owns it. Instruments: inflows, cohort survival,
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
import weather_issue_boundary as IB
import weather_backfill_exposure as BE   # backfill denominator, single source of truth

CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()

import corpus_store as CS

# The corpus comes from the observation store, not from globbing a directory and not from a
# prev_corpus tree unpacked out of git. Two consequences worth naming:
#   * WEATHER_OBSERVED_AT pins which observations count, so a past issue is reproducible by
#     argument rather than by checking out the commit its corpus was committed in.
#   * There is no prev_corpus. The previous issue's state is a timestamp, so a mid-day catch-up
#     pull no longer moves this issue's baseline -- which under the old scheme it silently did,
#     because the baseline was `git archive HEAD data/posts`.
CON = CS.build_index()
OBSERVED_AT = float(os.environ["WEATHER_OBSERVED_AT"]) if os.environ.get("WEATHER_OBSERVED_AT") \
    else None
PREV_AT = float(os.environ["WEATHER_PREV_OBSERVED_AT"]) if os.environ.get("WEATHER_PREV_OBSERVED_AT") \
    else IB.previous_issue_observed_at(_c)

# Issue #14 made the placeholder-free parse the published currency (issue #13 measured the
# defect: 1f916 substitutes a fixed body for a collapsed item instead of deleting it, and that
# body clears MIN_CHARS). WEATHER_KEEP_PLACEHOLDERS=1 reproduces issues #1-#13.
EXCLUDE_PH = CS.exclude_placeholders_default()
NEW = CS.weather_items(CON, cutoff=CUTOFF, observed_at=OBSERVED_AT)
# prev_last is the last item the PREVIOUS observation physically held. It still defines the
# backfill comparison (see below), and it is now a query rather than a max() over an unpacked tree.
prev_last = CON.execute("SELECT MAX(created_at) FROM observations WHERE first_seen_at <= ? "
                        "AND n_chars >= ?", (PREV_AT, CS.MIN_CHARS)).fetchone()[0]
PREV = None                                              # kept out of memory on purpose
# The issue window starts at the previous issue's CUTOFF, not the previous pull's last item; see
# analysis/weather_issue_boundary.py. prev_last still defines the BACKFILL comparison below, which
# genuinely is about what the previous pull physically held.
WIN_START, WIN_PROV = IB.issue_window_start(_c, prev_last)
_n_prev = CON.execute("SELECT COUNT(DISTINCT item_key) FROM observations WHERE first_seen_at <= ?"
                     " AND n_chars >= ?", (PREV_AT, CS.MIN_CHARS)).fetchone()[0]
print(f"prev observation {dt.datetime.utcfromtimestamp(PREV_AT):%m-%d %H:%M} "
      f"({_n_prev} items, last {dt.datetime.utcfromtimestamp(prev_last):%m-%d %H:%M}), "
      f"this-issue items {len(NEW)} (cutoff {_c} 00:00 UTC)", flush=True)

day = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
days = sorted({day(t) for t, _, _, _ in NEW})

# --- feed-lag / backfill instrument: items that existed-in-time at the previous pull but were
# invisible to it (timestamp <= prev pull's last item, absent from prev_corpus). Quantifies the
# undercount of trailing-day numbers so the newest day is reported as provisional. ---
# ...and it is now a QUERY over recorded observations rather than a diff of two corpus trees.
_bf = CS.backfill(CON, prev_at=PREV_AT, this_at=OBSERVED_AT or 9e18, basis="prev_last_item")
backfill = [(b["created_at"], tuple(b["item_key"].split(":", 1)), b["author"]) for b in _bf]
bf_day = {}
for b in _bf: bf_day[day(b["created_at"])] = bf_day.get(day(b["created_at"]), 0) + 1
# "revealed" = the backfilled item is that author's first observation anywhere
bf_authors = {b["author"] for b in _bf if b["reveals_author"]}
lags_h = sorted((prev_last - t) / 3600 for t, k, a in backfill)
feed_lag = {"backfilled_items": len(backfill), "by_day": bf_day,
            "new_authors_revealed": len(bf_authors),
            # proper median: lags_h[len//2] is the upper-middle value and is only the median for
            # odd n. Issue #12 was the first even-count backfill and published 7.82 for a set whose
            # median is 3.97 -- with the three-and-three split that made the reading, not a summary.
            "item_age_at_missed_pull_hours": {"median": round(float(np.median(lags_h)), 2) if lags_h else None,
                                              "p90": round(lags_h[int(len(lags_h)*0.9)], 2) if lags_h else None},
            "note": "trailing-day counts are provisional: this pull's view of its final hours will be revised upward by roughly this issue's backfill rate"}
# Both bases in the record, not one in the record and one in the prose. prev_last_item reproduces
# the series; prev_run is the stricter reading (the pull ran at time T, so anything created before
# T should have been caught). The max age is published beside the median because what makes a
# backfill a pull-boundary RACE rather than a lagging feed is that its OLDEST item is minutes old.
feed_lag["backfilled_items_prev_run_basis"] = len(
    CS.backfill(CON, prev_at=PREV_AT, this_at=OBSERVED_AT or 9e18, basis="prev_run"))
feed_lag["item_age_at_missed_pull_hours"]["max"] = round(max(lags_h), 3) if lags_h else None
# The count alone is not comparable across issues. A backfilled item can only come from the
# stretch the previous pull already reached into -- (previous issue's cutoff, its last item] --
# whose width is that pull's MARGIN, not this issue's window width. Issue #14 normalised by window
# items and so halved its own rate by covering two calendar days. See weather_backfill_exposure.
feed_lag["exposure"] = BE.cell(CON, _c, PREV_AT, _bf, observed_at=OBSERVED_AT)

# --- content-mutation check (issue-3 watch item #4): items present in BOTH corpora under the
# same id whose TEXT changed after publication. id-keyed caches (claims, allocation labels)
# cannot see this and retain stale values until the item is re-processed; observed moving
# frozen-day register cells at the 4th decimal between issues. ---
# The store records an edit as a ROW (version='edit'), so this is a window query. Under the old
# scheme it required holding both corpora in memory and hashing every item in each -- which is the
# only reason the pipeline needed a full re-read of every thread every issue.
_ed = CS.edits(CON, since=PREV_AT, until=OBSERVED_AT or 9e18)
edited = [(e["created_at"], tuple(e["item_key"].split(":", 1)), e["author"]) for e in _ed]
ed_day = Counter(day(e["created_at"]) for e in _ed)
_prev_chars = {}
for e in _ed:
    r = CON.execute("SELECT n_chars FROM observations WHERE item_key = ? AND first_seen_at < ? "
                    "ORDER BY first_seen_at DESC LIMIT 1", (e["item_key"], e["first_seen_at"])).fetchone()
    if r:
        _prev_chars[e["item_key"]] = r[0]
_now_chars = {r["item_key"]: r["n_chars"] for r in CS.items_at(CON, cutoff=CUTOFF,
                                                              observed_at=OBSERVED_AT)}
delta_chars = [_now_chars[k] - _prev_chars[k] for k in _prev_chars if k in _now_chars]
_items_compared = _n_prev
feed_lag["content_mutations"] = {
    "items_compared": _items_compared,
    "edited_items": len(edited),
    "by_day": dict(sorted(ed_day.items())),
    "authors_affected": len({a for _, _, a in edited}),
    "char_delta": {"median": float(np.median(delta_chars)) if delta_chars else None,
                   "min": min(delta_chars) if delta_chars else None,
                   "max": max(delta_chars) if delta_chars else None},
    "edited_keys": [e["item_key"] for e in _ed],
    # An edit is only detectable in a thread re-read AFTER the previous issue, so the audit's
    # denominator is coverage since that issue's pull -- not the rolling 24 h freshness figure,
    # and not an assumed full re-read. Publish it beside the count or the count means nothing.
    "audit_coverage": CS.verified_since(CON, PREV_AT),
    "note": "post-publication text edits; invisible to id-keyed claim/allocation caches. weather_gpu.py evicts these keys and re-processes them."}

out = {"cutoff_utc": _c + "T00:00:00Z", "issue_window_start_utc":
       dt.datetime.utcfromtimestamp(WIN_START).strftime("%Y-%m-%d %H:%M"),
       "issue_window_basis": WIN_PROV,
       "corpus": {"items": len(NEW), "posts": sum(1 for _, k, _, _ in NEW if k[0] == "post"),
                  "authors": len({a for _, _, _, a in NEW}), "days": days,
                  "issue_window_items": sum(1 for t, _, _, _ in NEW if t >= WIN_START),
                  "issue_window_items_old_prev_pull_basis": sum(1 for t, _, _, _ in NEW if t > prev_last)}}

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
# Only self_bits and cond_win_bits are read below, so only those are computed. cond_full rebuilt a
# level-19 dictionary over the WHOLE history once per 25-item bucket -- the quadratic term that made
# this stage ~55 min at issue #11 -- and nothing in the weather series has ever consumed it; it
# belongs to the standalone zstd pass. Both remaining columns are prefix-stable, so rows carry over
# from the previous issue and only the new tail is computed. The cache is keyed kind:id like every
# other cache here, and is discarded whole if the compression parameters move.
_ZCACHE = S / "zstd_row_cache_agent.json"
import zstandard as _zstd
# The compressor VERSION belongs in the key: an upgrade that changes compressed sizes would splice
# old-prefix and new-tail values into one published series with nothing to detect it. That is the
# only invalidation path the key+hash+position check cannot see.
_ZPARAMS = {"level": Args.level, "window_bytes": Args.window_bytes, "bucket": Args.bucket,
            "zstd": _zstd.__version__}
_zc = json.load(open(_ZCACHE)) if _ZCACHE.exists() else {}
_reuse = _zc.get("rows", {}) if _zc.get("params") == _ZPARAMS else {}
if _zc and not _reuse:
    print("zstd cache: parameters changed, discarding", flush=True)
rows = Z.compute_metrics(mk, Args(), columns=("self", "cond_win"), reuse=_reuse)
# A pinned re-run (WEATHER_OBSERVED_AT) describes a PAST corpus; writing its rows back would roll
# the live pipeline's cache to that state. Values could not go wrong -- the prefix check is exact --
# but the next live run would recompute a tail it already had.
if OBSERVED_AT is None:
    json.dump({"params": _ZPARAMS, "rows": {f"{r['kind']}:{r['id']}": r for r in rows}},
              open(_ZCACHE, "w"))
else:
    print("pinned run (WEATHER_OBSERVED_AT set): zstd cache left untouched", flush=True)
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
