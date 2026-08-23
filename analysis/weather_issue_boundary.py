#!/usr/bin/env python3
"""Where one weather issue ends and the next begins. Stdlib only, so both halves can import it.

Two boundary questions keep coming up, both have subtle wrong answers, and they were previously
answered inline in three scripts that run under two different Python environments (weather_cpu.py
in .venv, weather_gpu.py in the conda env). This module is the single source for both and imports
nothing heavy so either environment can use it.

1. WHICH ISSUES ARE "BEFORE" THIS ONE.  The obvious filter -- every issue dir sorting below the
   current cutoff -- is wrong once the current issue's own directory exists, because an issue
   dated D is produced with cutoff D+1 and therefore sorts below its own cutoff. That made the
   pipeline non-idempotent (found at issue #8: a re-run moved the pooled newcomer window from
   145/1,835 to 17/1,207 and made the retro-movement audit compare the issue against itself).

2. WHERE THE ISSUE WINDOW STARTS.  Issues #1-#8 used the previous pull's LAST ITEM. That silently
   assumed the previous pull ran shortly after its own cutoff, which was never a stable property:
   the derived margins for issues #3-#7 are 0.2, 5.2, 4.5, 2.9 and 3.0 h (see
   weather_cutoff_margin.history() -- do not quote a remembered average, this docstring carried
   "~3 h" until issue #10). It also left a small permanent hole (issue #8 disclosed 191 items of
   08-20 that entered every full-pool cell and no issue's window cells, ever).

   Issue #8 ran a day late and pulled 23.7 h after its cutoff, which swept up nearly all of the
   NEXT issue's day. Under the old rule issue #9's window would have been **27 items** spanning 18
   minutes instead of a calendar day, and ~800 items of 08-21 would have fallen into that hole.

   So the window now starts at the previous published issue's **CUTOFF**, not its pull. That is
   the boundary the analysis actually used: everything after it is new to the SERIES, whether or
   not the previous pull physically happened to hold it. It also makes a window exactly the set of
   days the issue adds, which is what the reports have always called it ("one-day window").

   NOT strictly like-for-like with issues #1-#8: their windows omitted the few hours between their
   cutoff and their pull, so they covered ~87% of a day where a cutoff-based window covers all of
   it. Same KIND (one calendar day), slightly different extent; comparisons should say so.
"""
import datetime as dt
import json
from pathlib import Path

WEATHER = Path("/home/dan/personal/memetic/results/weather")
_epoch = lambda d: d.replace(tzinfo=dt.timezone.utc).timestamp()


def cutoff_epoch(cutoff_str):
    """'YYYY-MM-DD' -> that date's midnight UTC as epoch seconds (the exclusive upper bound)."""
    return _epoch(dt.datetime(*map(int, cutoff_str.split("-"))))


def own_issue_date(cutoff_str):
    """-> the date the issue with this cutoff REPORTS on, i.e. cutoff - 1 day."""
    return (dt.datetime(*map(int, cutoff_str.split("-"))) - dt.timedelta(days=1)).strftime("%Y-%m-%d")


def published_issues_before(cutoff_str, root=WEATHER):
    """-> published issue dirs strictly before the issue being produced, newest first."""
    own = own_issue_date(cutoff_str)
    return sorted((q for q in Path(root).glob("20*-*-*")
                   if (q / "results.json").exists() and q.name < cutoff_str and q.name != own),
                  reverse=True)


def issue_window_start(cutoff_str, prev_last=None, root=WEATHER):
    """-> (start epoch, provenance dict) for this issue's window. See note 2 above.

    prev_last (the previous pull's last item) is used only for the fallback and for reporting how
    much the definition change is worth this issue.
    """
    dirs = published_issues_before(cutoff_str, root)
    if not dirs:
        return prev_last, {"basis": "previous pull's last item (no published issue precedes this one)"}
    prev = json.load(open(dirs[0] / "results.json"))
    start = _epoch(dt.datetime.strptime(prev["cutoff"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=None))
    p = {"basis": "previous published issue's CUTOFF (changed at issue #9; issues #1-#8 used the "
                  "previous pull's last item)",
         "start_utc": dt.datetime.fromtimestamp(start, dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
         "from_issue": prev.get("issue"), "source": str(dirs[0] / "results.json")}
    if prev_last is not None:
        p["prev_pull_last_item_utc"] = dt.datetime.fromtimestamp(
            prev_last, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
        p["hours_the_change_recovers"] = round((prev_last - start) / 3600, 2)
    return start, p


def window_coverage_history(root=WEATHER):
    """-> per-issue: how much of its own final day each published issue's window actually covered.

    This is the evidence that the pre-#9 window rule was not a stable definition at all. Because
    the window started at the previous PULL's last item, its extent tracked whatever time of day
    that pull happened to run:

      * issues #3 and #4 pulled just after midnight, so their windows began 00:05-00:08 and covered
        97-99% of the day -- i.e. they were cutoff-based in all but name;
      * issues #6, #7 and #8 pulled at 02:45-04:31 and covered only ~70%;
      * issues #2 and #5 followed multi-day gaps, so their windows spanned more than one day
        (coverage over 100% against a single day's item count, and NOT one-day windows at all).

    So "one-day window" has meant anywhere from 70% to 99% of a day, drifting with pull time, and
    cross-issue window comparisons carried that variation silently. Anchoring the window to the
    previous issue's cutoff makes it exactly 100% every issue. The reports' like-for-like grouping
    of issues #4/#6/#7/#8 as "one-day windows" was therefore already approximate.
    """
    out = []
    for q in sorted(Path(root).glob("20*-*-*")):
        rj = q / "results.json"
        if not rj.exists():
            continue
        d = json.load(open(rj))
        w = (d.get("corpus") or {}).get("issue_window_items")
        day = q.name[5:]
        tot = ((d.get("structure") or {}).get("inflows") or {}).get(day, {}).get("items")
        out.append({"issue": d.get("issue"), "date": q.name, "window_items": w,
                    "final_day_items": tot,
                    "coverage_pct": (round(100 * w / tot, 1) if (w and tot) else None),
                    "window_start_utc": d.get("issue_window_start"),
                    "note": ("multi-day window (follows a gap); coverage >100% is against ONE day's "
                             "items and it is not a one-day window"
                             if (w and tot and w > tot * 1.05) else None)})
    return out


if __name__ == "__main__":
    import sys
    print(json.dumps(window_coverage_history(), indent=1) if "--json" in sys.argv else "")
    if "--json" not in sys.argv:
        print(f"{'issue':22s} {'window':>7s} {'day':>7s} {'cover':>7s}  window start")
        for r in window_coverage_history():
            cov = "-" if r["coverage_pct"] is None else f"{r['coverage_pct']:.1f}%"
            print(f"{str(r['issue']):22s} {str(r['window_items']):>7s} "
                  f"{str(r['final_day_items']):>7s} {cov:>7s}  {r['window_start_utc']}"
                  + ("   <- multi-day" if r["note"] else ""))
