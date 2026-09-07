#!/usr/bin/env python3
"""The idea series' primary cell: per-issue median window level, on one basis.

WHY THIS EXISTS. `window_level_median` has been the idea series' PRIMARY cell since issue #15
(issue #14's watch item #4 demoted the sub-forth rate, because counting windows against an anchor
that sits inside the series' own distribution is a step readout of a continuous level). It has
also been assembled by hand in every issue since. Issue #21 carries a PRE-REGISTERED partition on
this exact number -- at or under 0.1255 is a third consecutive fall, above 0.1269 puts the level
back over the forth anchor -- and the runbook's rule is that a load-bearing number must be
reproducible from `analysis/` before a reviewer sees it. A pre-registered trigger read off a
hand-built table is the one number in an issue that cannot be allowed to live in a scratch file.

TWO COLUMNS, AND THEY ARE NOT INTERCHANGEABLE.

  median            each issue's OWN published series. Issues #1-#13 are with-placeholder,
                    #14-#20 are placeholder-free, #21+ exclude every platform-substituted body.
                    It is the continuity row and must not be compared across those boundaries.
  median_one_basis  every issue's windows recomputed from THIS issue's series, so the whole
                    column is one currency. This is the row a cross-issue reading uses.

WINDOW ASSIGNMENT. A window belongs to the issue whose cutoff FIRST covers it -- the same rule
`per_issue_dip_rate_rebaselined` uses. Windows are stamped "%m-%d %H:%M" with no year, which is
unambiguous only because the corpus is one month long; the year comes from the issue dates.

THE NEWEST ROW IS PROVISIONAL. It gains windows next issue as the rolling window fills, so a dip
in the newest one-basis row is not drift. See [[rolling-window-tail-is-provisional]].

Usage:
  MEMETIC_WORKDIR=... python3 analysis/weather_idea_median.py            # table + this issue
  MEMETIC_WORKDIR=... python3 analysis/weather_idea_median.py --json     # machine-readable
"""
import argparse, datetime as dt, json, os, statistics as st, sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
sys.path.insert(0, str(R / "analysis"))
import weather_issue_boundary as IB                                      # noqa: E402

FORTH = 0.1269          # frozen anchor; never re-measured


def _stamp(s, year):
    """'09-03 22:04' -> epoch seconds. The series carries no year; the issue dates do."""
    m, d = s.split()[0].split("-")
    hh, mm = s.split()[1].split(":")
    return dt.datetime(year, int(m), int(d), int(hh), int(mm),
                       tzinfo=dt.timezone.utc).timestamp()


def published_issues(root=IB.WEATHER, before=None):
    """-> [(issue_label, issue_date, cutoff_epoch)] oldest first, from the published record.

    `before` EXCLUDES the issue being assembled and anything after it. Without it an issue that has
    already written its own results.json is read as its own predecessor, and `table()` then appends
    `this_issue` a second time -- the pipeline-self-reference hazard. Issue #21 shipped a draft with
    two #21 rows in window_level_median, the first carrying nulls, which would have made #22 read a
    null continuity cell; and its rebaselined row pooled the same 46 windows twice (24.4 -> 25.1).
    """
    out = []
    for p in sorted(Path(root).iterdir()):
        if before is not None and p.name >= before:
            continue
        f = p / "results.json"
        if not f.is_dir() and f.exists():
            d = json.load(open(f))
            # The cutoff IS issue date + 1 day by definition, and issue #1 predates the published
            # field. Derive it from the directory name and use the published value only to assert
            # the two agree, so a typo in either surfaces here rather than silently shifting a
            # window into the wrong issue.
            date = dt.date.fromisoformat(p.name) + dt.timedelta(days=1)
            cut = IB.cutoff_epoch(date.isoformat())
            if d.get("cutoff") and IB.cutoff_epoch(d["cutoff"][:10]) != cut:
                raise SystemExit(f"{p.name}: published cutoff {d['cutoff']} is not issue date + 1")
            out.append((d["issue"].split("(")[-1].rstrip(")").strip() or d["issue"], p.name, cut))
    return out


def assign(t_utc, vendi, cutoffs, year=2026):
    """-> {issue_date: [window levels]}, each window to the first cutoff that covers it."""
    out = {}
    for s, v in zip(t_utc, vendi):
        t = _stamp(s, year)
        for label, date, cut in cutoffs:
            if t < cut:
                out.setdefault(date, []).append(v)
                break
    return out


def table(series=None, this_issue=None, workdir=None):
    """-> [{issue, date, n_windows_one_basis, median_one_basis, median, n_windows, anchor_forth}].

    `median`/`n_windows` are read from each issue's published record (the continuity column);
    the one-basis pair is recomputed here from the current series.
    """
    S_ = Path(workdir or S)
    if series is None:
        series = json.load(open(S_ / "weather_gpu_out.json"))["rolling_series_bge"]
    issues = published_issues(before=this_issue["date"] if this_issue else None)
    if this_issue:                                    # the unpublished issue being assembled
        issues = issues + [(this_issue["issue"], this_issue["date"],
                            IB.cutoff_epoch(this_issue["cutoff"][:10]))]
    buckets = assign(series["t_utc"], series["vendi_over_W"], issues)

    prev_pub = {}
    for _, date, _ in issues:
        f = IB.WEATHER / date / "results.json"
        if f.exists():
            for row in json.load(open(f))["idea_time_series"].get("window_level_median", []):
                prev_pub.setdefault(row["date"], row)

    rows = []
    for label, date, _ in issues:
        w = buckets.get(date, [])
        pub = prev_pub.get(date, {})
        rows.append({"issue": label, "date": date,
                     "n_windows": pub.get("n_windows"), "median": pub.get("median"),
                     "anchor_forth": FORTH,
                     "median_one_basis": round(st.median(w), 4) if w else None,
                     "n_windows_one_basis": len(w)})
    return rows


def _stats(w):
    import statistics as _st
    if not w:
        return {}
    q = sorted(w)
    n = len(q)
    iqr = q[int(0.75 * (n - 1))] - q[int(0.25 * (n - 1))]
    return {"new_windows": n,
            "new_below_forth": sum(1 for x in w if x < FORTH),
            "new_below_forth_pct": round(100 * sum(1 for x in w if x < FORTH) / n, 1),
            "new_window_mean": round(_st.mean(w), 4),
            "new_window_median": round(_st.median(w), 4),
            "new_window_sd": round(_st.pstdev(w), 4) if n > 1 else 0.0,
            "new_window_iqr": round(iqr, 4),
            "new_window_min": round(min(w), 4), "new_window_max": round(max(w), 4)}


def dip_rates(series, this_issue, prev_published):
    """The DEMOTED footnote cell, kept for continuity (see `primary_cell`).

    -> (per_issue_dip_rate, per_issue_dip_rate_rebaselined). The first keeps every prior issue's
    OWN published row and appends this issue's; the second recomputes every issue on this issue's
    series. They differ by a few windows by construction -- the first splits by shared-prefix
    length, the second assigns each window to the issue whose cutoff first covers it. Quote one,
    never a mixture.
    """
    issues = published_issues(before=this_issue["date"]) + [
        (f"issue {this_issue['issue']}", this_issue["date"],
         IB.cutoff_epoch(this_issue["cutoff"][:10]))]
    buckets = assign(series["t_utc"], series["vendi_over_W"], issues)
    reb, pooled = [], []
    for label, date, _ in issues:
        w = buckets.get(date, [])
        pooled += w
        row = {"issue": label, **_stats(w)}
        row["pooled_below_forth_pct"] = round(
            100 * sum(1 for x in pooled if x < FORTH) / len(pooled), 1) if pooled else None
        reb.append(row)

    own = list(prev_published)
    w = buckets.get(this_issue["date"], [])
    allw = series["vendi_over_W"]
    own.append({"issue": this_issue["issue"], "date": this_issue["date"],
                "windows": len(allw), "new_windows": len(w), "forth": FORTH,
                "pooled_below_forth_pct": round(100 * sum(1 for x in allw if x < FORTH) / len(allw), 1),
                "new_below_forth": sum(1 for x in w if x < FORTH),
                "new_below_forth_pct": round(100 * sum(1 for x in w if x < FORTH) / len(w), 1) if w else None,
                "last_window": allw[-1], "new_window_mean": round(sum(w) / len(w), 4) if w else None,
                "last_t_utc": series["t_utc"][-1]})
    return own, reb


def prefix_drift(series, prev_series, prev_t=None):
    """Windows the previous issue already published that this issue's series moves.

    ALIGNED ON TIMESTAMP, NOT INDEX. Through issue #20 the item stream only ever GAINED items, so
    `vendi_over_W[i]` named the same window in both issues and a positional diff was correct.
    Issue #21's currency change REMOVES items (49 platform-substituted bodies), which shifts every
    later window's position: index i no longer names the same window in the two series, and a
    positional diff reports ~97% of windows moved when almost none did. Windows are keyed by their
    end timestamp, which the basis change does not move.

    A window present in one series and absent from the other is not drift -- it is a window whose
    end item left the currency -- so it is counted separately rather than as a move.
    """
    prev_t = prev_t or []
    if not prev_t:                       # no timestamps published: cannot align, so say so
        return {"windows_moved": None, "of_shared": None, "crossed_forth": None, "detail": [],
                "read": "previous issue published no window timestamps; alignment impossible."}
    prev = dict(zip(prev_t, prev_series))
    now = dict(zip(series["t_utc"], series["vendi_over_W"]))
    shared = [t for t in prev if t in now]
    detail = []
    for t in shared:
        a, b = prev[t], now[t]
        if abs(a - b) > 1e-9:
            detail.append({"t_utc": t, "prev": a, "now": b, "delta": round(b - a, 4),
                           "crossed_forth": (a < FORTH) != (b < FORTH)})
    detail.sort(key=lambda x: -abs(x["delta"]))
    return {"windows_moved": len(detail), "of_shared": len(shared),
            "crossed_forth": sum(1 for x in detail if x["crossed_forth"]),
            "windows_only_in_prev": len(prev) - len(shared),
            "windows_only_in_this": len(now) - len(shared),
            "largest_move": detail[0]["delta"] if detail else 0.0,
            "detail": detail[:40],
            "read": "a moved window is a re-derivation of an already-published level, not drift in "
                    "the square; only `crossed_forth` moves can change a published dip count. "
                    "`windows_only_in_prev` are windows whose end item left the currency under "
                    "this issue's basis change -- absence, not movement."}


def threshold_sensitivity(rows, prev_published):
    """Median and sub-anchor rate side by side, so a rate move can be read against a level move."""
    out = list(prev_published)
    r = rows[-1]
    prev = out[-1] if out else {}
    row = {"issue": r["issue"], "date": r["date"], "n_windows": r["n_windows_one_basis"],
           "median": r["median_one_basis"], "anchor": FORTH}
    if prev.get("median") is not None and row["median"] is not None:
        row["median_shift_vs_prev"] = round(row["median"] - prev["median"], 4)
        row["prev_rate_pct"] = prev.get("rate_pct")
    out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--issue"), ap.add_argument("--date"), ap.add_argument("--cutoff")
    a = ap.parse_args()
    this = {"issue": a.issue, "date": a.date, "cutoff": a.cutoff} if a.date else None
    rows = table(this_issue=this)
    if a.json:
        print(json.dumps(rows, indent=1)); return
    print(f"{'issue':>6} {'date':>12} {'n_win':>6} {'median':>8} | "
          f"{'n_win_1b':>9} {'median_1b':>10}  vs forth {FORTH}")
    for r in rows:
        m1 = r["median_one_basis"]
        mark = "" if m1 is None else ("  BELOW" if m1 <= FORTH else "")
        print(f"{r['issue']:>6} {r['date']:>12} {str(r['n_windows']):>6} "
              f"{str(r['median']):>8} | {r['n_windows_one_basis']:>9} "
              f"{str(m1):>10}{mark}")
    ones = [r["median_one_basis"] for r in rows if r["median_one_basis"] is not None]
    if len(ones) >= 3:
        print(f"\nlast three one-basis medians: {ones[-3]} -> {ones[-2]} -> {ones[-1]}")


if __name__ == "__main__":
    main()
