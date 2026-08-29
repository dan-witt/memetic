#!/usr/bin/env python3
"""The denominator for a backfill count.

A backfilled item is one the PREVIOUS pull should have caught and did not. It can therefore only
come from the stretch that pull's coverage had already reached: items created after the previous
issue's CUTOFF (so they land in this issue's window) but at or before the previous corpus's last
item. The width of that stretch is set by the previous pull's MARGIN past its own cutoff -- 3.33 h
at issue #14, 1.58 h at #15 -- and has nothing to do with how many days this issue's window spans.

Issue #14 normalised by window items instead, and that denominator moves for the wrong reason: its
window was two calendar days, so the same boundary race divided by twice as many items and the
rate halved. This module publishes the exposure denominator alongside the count so the two are
separable, and derives the same pair for every published issue so the series is like-for-like.

Backfill outside the exposure stretch is reported separately, not folded in: an item older than
the previous issue's cutoff that only appears now lands on an ALREADY PUBLISHED day, which is a
different and more serious event than a boundary race. Issue #12 is the one issue whose backfill
was not the race.

Usage: WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_backfill_exposure.py
"""
import datetime as dt, json, os, sys
from pathlib import Path

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import corpus_store as CS
import weather_issue_boundary as IB
from weather_cutoff_margin import _parse_stamp as _stamp   # tolerates issues #1-#3's prose stamps


def exposure(con, prev_at, window_start, observed_at=None, min_chars=CS.MIN_CHARS):
    """-> {prev_last_item_utc, exposure_items, exposure_hours} for one issue boundary.

    `window_start` is the previous issue's cutoff (weather_issue_boundary.issue_window_start).
    """
    prev_last = con.execute(
        "SELECT MAX(created_at) FROM observations WHERE first_seen_at <= ? AND n_chars >= ?",
        (prev_at, min_chars)).fetchone()[0]
    if prev_last is None or prev_last <= window_start:
        return {"prev_last_item_utc": None, "exposure_items": 0, "exposure_hours": 0.0}
    n = con.execute(
        "SELECT COUNT(DISTINCT item_key) FROM observations WHERE created_at > ? AND "
        "created_at <= ? AND n_chars >= ? AND first_seen_at <= ?",
        (window_start, prev_last, min_chars, observed_at or 9e18)).fetchone()[0]
    return {"prev_last_item_utc": dt.datetime.fromtimestamp(prev_last, dt.timezone.utc)
                                    .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exposure_items": n,
            "exposure_hours": round((prev_last - window_start) / 3600, 2)}


def cell(con, cutoff_str, prev_at, backfill_rows, observed_at=None):
    """The per-issue block: count, exposure, rate, and how much fell OUTSIDE the exposure."""
    start, _ = IB.issue_window_start(cutoff_str, prev_last=None)
    ex = exposure(con, prev_at, start, observed_at)
    inside = [b for b in backfill_rows if b["created_at"] > start]
    out = dict(ex)
    out["window_start_utc"] = dt.datetime.fromtimestamp(start, dt.timezone.utc)\
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    out["backfilled_items"] = len(backfill_rows)
    out["backfilled_in_exposure"] = len(inside)
    out["backfilled_on_published_days"] = len(backfill_rows) - len(inside)
    out["per_1000_exposure_items"] = (round(1000 * len(inside) / ex["exposure_items"], 2)
                                      if ex["exposure_items"] else None)
    out["note"] = ("exposure = items created in (previous issue's cutoff, previous corpus's last "
                   "item]; its width is the previous pull's margin, not this issue's window width")
    return out


def history(root=IB.WEATHER):
    """The same pair for every published issue, so counts across issues are comparable."""
    con = CS.build_index()
    dirs = sorted(q for q in Path(root).glob("20*-*-*") if (q / "results.json").exists())
    rows, prev = [], None
    for i, q in enumerate(dirs):
        d = json.load(open(q / "results.json"))
        cut = d.get("cutoff")
        pa = d.get("pull_at")
        if prev is None or not cut or not pa:
            prev = d; rows.append({"issue": f"#{i+1}", "date": q.name, "exposure_items": None,
                                   "backfilled_items": (d.get("feed_lag") or {}).get("backfilled_items")})
            continue
        prev_at, this_at = _stamp(prev.get("pull_at")), _stamp(pa)
        if prev_at is None or this_at is None:
            prev = d; rows.append({"issue": f"#{i+1}", "date": q.name, "exposure_items": None,
                                   "backfilled_items": (d.get("feed_lag") or {}).get("backfilled_items")})
            continue
        bf = CS.backfill(con, prev_at=prev_at, this_at=this_at, basis="prev_last_item")
        r = cell(con, cut[:10], prev_at, bf, observed_at=this_at)
        r.update({"issue": f"#{i+1}", "date": q.name,
                  "published_backfilled_items": (d.get("feed_lag") or {}).get("backfilled_items")})
        rows.append(r)
        prev = d
    return rows


if __name__ == "__main__":
    rows = history()
    print(f"{'issue':6s} {'date':12s} {'bf':>4s} {'pub':>4s} {'expo':>6s} {'hrs':>6s} "
          f"{'/1000 expo':>10s} {'on published days':>18s}")
    for r in rows:
        print(f"{r['issue']:6s} {r['date']:12s} "
              f"{r.get('backfilled_items','-')!s:>4s} {r.get('published_backfilled_items','-')!s:>4s} "
              f"{r.get('exposure_items','-')!s:>6s} {r.get('exposure_hours','-')!s:>6s} "
              f"{r.get('per_1000_exposure_items','-')!s:>10s} "
              f"{r.get('backfilled_on_published_days','-')!s:>18s}")
    S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
    json.dump(rows, open(S / "weather_backfill_exposure_out.json", "w"), indent=1)
    print("saved", S / "weather_backfill_exposure_out.json")
