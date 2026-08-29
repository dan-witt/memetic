#!/usr/bin/env python3
"""Sub-forth dip rate, per issue rather than pooled — and a drift assertion on the rolling series.

Issues #4 and #5 reported the share of rolling claim-Vendi/W windows sitting below the forth
anchor as a POOLED figure over the whole series to date. That is a composition statistic in the
same family as the fixed-horizon permeability running mean (see weather_permeability_control.py):
each window's value is frozen once computed, so the pooled share moves only as new windows are
appended, and it lags the current level by however much history it is averaging over. The cell
that answers "how often is the community dipping below the nearest anchor NOW?" is the rate over
the windows an issue actually added.

Also asserts what makes that decomposition valid: the shared prefix of two consecutive issues'
series must be bit-identical. Claims are cached by kind:id and the windowing is deterministic, so
any mismatch means the past moved (a re-claimified item, a corpus edit, a windowing change) and
the per-issue rates are not comparable until it is explained.

Usage: python3 analysis/weather_dip_rate.py            (all published issues)
"""
import datetime as dt
import json, sys
from pathlib import Path

W = Path("/home/dan/personal/memetic/results/weather")


def _issues(root=W):
    """[(tag, issue-date)] for every published issue — derived, so it needs no edit per issue."""
    ds = sorted(q.name for q in Path(root).glob("20*-*-*") if (q / "results.json").exists())
    return [(f"#{i+1}", d) for i, d in enumerate(ds)]


ISSUES = _issues()


def series(date):
    p = W / date / "results.json"
    if not p.exists(): return None
    ts = json.load(open(p)).get("idea_time_series")
    return ts if ts and ts.get("vendi_over_W") else None


def rates(issues=ISSUES):
    out, prev = [], None
    for tag, date in issues:
        ts = series(date)
        if not ts: continue
        v, t = ts["vendi_over_W"], ts["t_utc"]
        forth = ts["anchor_levels"]["forth"]
        # A drift COUNT is not actionable on its own -- "the past moved" needs to say which
        # windows, by how much, and whether any crossed the anchor, because those three facts
        # decide whether the per-issue decomposition survives. Issue #7 drifted in exactly the 3
        # windows containing one post-publication edit (post:1197, 2384 -> 246 chars), none of
        # which crossed forth, so the published dip COUNTS were untouched.
        drift_idx = ([] if prev is None else
                     [i for i in range(min(len(v), len(prev))) if v[i] != prev[i]])
        drift = len(drift_idx)
        drift_detail = [{"i": i, "t_utc": t[i], "prev": prev[i], "now": v[i],
                         "delta": round(v[i] - prev[i], 5),
                         "crossed_forth": (prev[i] < forth) != (v[i] < forth)}
                        for i in drift_idx]
        new = v[len(prev):] if prev is not None else v
        row = {"issue": tag, "date": date, "windows": len(v), "new_windows": len(new),
               "forth": forth,
               "pooled_below_forth_pct": round(100 * sum(1 for x in v if x < forth) / len(v), 1),
               "new_below_forth": sum(1 for x in new if x < forth),
               "new_below_forth_pct": (round(100 * sum(1 for x in new if x < forth) / len(new), 1)
                                       if new else None),
               "last_window": v[-1], "new_window_mean": round(sum(new) / len(new), 4) if new else None,
               "prefix_drift_vs_prev": drift, "prefix_drift_detail": drift_detail,
               "prefix_drift_crossed_forth": sum(1 for x in drift_detail if x["crossed_forth"]),
               "last_t_utc": t[-1]}
        out.append(row); prev = v
    return out


def rebaselined_rates(series, t_utc, anchor, issues=None):
    """Per-issue dip rates recomputed on ONE series, so every issue is on the same basis.

    `rates()` reads each issue's own published series, which is correct while the instrument is
    constant and wrong across a currency change: issue #14 excluded moderation placeholders, so its
    cell was computed on a different corpus from #1-#13's and the two cannot be compared. This
    assigns every window of the CURRENT series to the issue that first published a cutoff above it,
    which needs no window-count arithmetic and survives the boundaries shifting when items are
    dropped.

    Returns the full back-series under the current currency -- the republication issue #13's watch
    item #2 asked for.

    THE NEWEST ISSUE'S ROW IS PROVISIONAL. A 120-item window needs 120 items, so the trailing
    items of an issue's corpus cannot form one until the next issue's items arrive -- and those
    late windows are CENTRED before the issue's own cutoff, so they land in its bucket. Issue #14
    published 115 windows for itself and reads 117 here, with a bit-identical shared prefix. That
    is the construction, not drift: expect the newest row to gain a window or two next issue, and
    do not read a change of that size in the newest row as a movement.
    """
    issues = issues or ISSUES
    cuts = [(tag, (dt.datetime.strptime(d, "%Y-%m-%d") + dt.timedelta(days=1)))
            for tag, d in issues]
    # window stamps carry no year; the corpus is inside one year, so borrow it from the cutoffs
    year = cuts[0][1].year
    stamps = [dt.datetime.strptime(f"{year}-{x}", "%Y-%m-%d %H:%M") for x in t_utc]
    rows, lo = [], 0
    for tag, cut in cuts:
        hi = lo
        while hi < len(stamps) and stamps[hi] < cut:
            hi += 1
        add = series[lo:hi]
        if add:
            n_below = sum(1 for v in add if v < anchor)
            import statistics as _st
            rows.append({"issue": tag, "new_windows": len(add), "new_below_forth": n_below,
                         "new_below_forth_pct": round(100 * n_below / len(add), 1),
                         "new_window_mean": round(sum(add) / len(add), 4),
                         # the cell promoted to primary at issue #15, on ONE basis. The
                         # threshold_sensitivity median reads each issue's OWN published series,
                         # so it mixes the pre-#14 and post-#14 currencies; this one does not.
                         "new_window_median": round(_st.median(add), 4),
                         "pooled_below_forth_pct": round(
                             100 * sum(1 for v in series[:hi] if v < anchor) / hi, 1)})
        lo = hi
    return rows


def threshold_sensitivity(issues=None, anchor_name="forth"):
    """Decompose a change in the dip RATE into a level shift and a shape change.

    The dip rate counts windows below a fixed anchor. That anchor sits INSIDE the rolling series'
    own distribution, so the rate is a step readout of a continuous level: a shift of a few
    thousandths moves many windows across the line without any change in how the windows are
    spread. Issue #14 found 27 of 30 sub-forth windows within 0.005 of the anchor.

    For each consecutive pair, this reports the issue's own added windows, their median, the
    observed rate, and the counterfactual rate after removing the median shift against the
    previous issue. If the counterfactual lands near the previous rate, the whole move was level.
    """
    import statistics as st
    issues = issues or ISSUES
    rows, prev = [], None
    for tag, date in issues:
        ts = series(date)
        if not ts:
            continue
        anchor = (ts.get("anchor_levels") or {}).get(anchor_name)
        cur = ts["vendi_over_W"]
        add = cur[len(prev["vendi_over_W"]):] if prev else cur
        if not add or anchor is None:
            prev = ts; continue
        med = st.median(add)
        rate = sum(1 for v in add if v < anchor) / len(add)
        row = {"issue": tag, "date": date, "n_windows": len(add), "median": round(med, 4),
               "anchor": anchor, "rate_pct": round(100 * rate, 1),
               "sub_anchor_within_0.005": sum(1 for v in add if 0 <= anchor - v < 0.005),
               "sub_anchor_n": sum(1 for v in add if v < anchor)}
        if prev is not None:
            padd = prev.get("_added")
            if padd:
                shift = med - st.median(padd)
                moved = [v - shift for v in add]
                row["median_shift_vs_prev"] = round(shift, 4)
                row["rate_pct_without_level_shift"] = round(
                    100 * sum(1 for v in moved if v < anchor) / len(moved), 1)
                row["prev_rate_pct"] = round(100 * sum(1 for v in padd if v < anchor) / len(padd), 1)
        ts["_added"] = add
        rows.append(row)
        prev = ts
    return rows


if __name__ == "__main__":
    if "--threshold" in sys.argv:
        import json as _j
        rows = threshold_sensitivity()
        print(f"{'issue':6s} {'n':>5s} {'median':>8s} {'rate%':>7s} {'shift':>8s} "
              f"{'rate% if level held':>20s} {'prev%':>7s}  near-anchor")
        for r in rows:
            print(f"{r['issue']:6s} {r['n_windows']:5d} {r['median']:8.4f} {r['rate_pct']:7.1f} "
                  f"{r.get('median_shift_vs_prev','-')!s:>8s} "
                  f"{r.get('rate_pct_without_level_shift','-')!s:>20s} "
                  f"{r.get('prev_rate_pct','-')!s:>7s}  "
                  f"{r['sub_anchor_within_0.005']}/{r['sub_anchor_n']} within 0.005")
        sys.exit(0)
    rows = rates()
    print(f"{'issue':6s} {'windows':>8s} {'new':>5s} {'pooled<forth':>13s} {'NEW<forth':>12s} "
          f"{'new mean':>9s} {'drift':>6s}")
    for r in rows:
        pct = "-" if r["new_below_forth_pct"] is None else f"{r['new_below_forth_pct']:.1f}%"
        print(f"{r['issue']:6s} {r['windows']:8d} {r['new_windows']:5d} "
              f"{r['pooled_below_forth_pct']:12.1f}% {pct:>12s} "
              f"{str(r['new_window_mean']):>9s} {r['prefix_drift_vs_prev']:6d}")
    bad = [r for r in rows if r["prefix_drift_vs_prev"]]
    print("\nshared-prefix drift: " + ("NONE — the past is stable, per-issue rates are comparable"
                                       if not bad else f"VIOLATED in {[r['issue'] for r in bad]}"))
    for r in bad:
        print(f"  {r['issue']}: {r['prefix_drift_vs_prev']} window(s) moved, "
              f"{r['prefix_drift_crossed_forth']} of them across the forth anchor "
              f"({'dip counts UNCHANGED' if not r['prefix_drift_crossed_forth'] else 'DIP COUNTS AFFECTED'})")
        for x in r["prefix_drift_detail"]:
            print(f"     window {x['i']} ({x['t_utc']}): {x['prev']} -> {x['now']} "
                  f"({x['delta']:+.5f}){'  CROSSED' if x['crossed_forth'] else ''}")
        print("     a contiguous run of ~3 windows is the signature of ONE edited item (W=120, "
              "stride 40); check feed_lag.content_mutations.edited_keys for the cause.")
    print("The pooled column averages over all history and lags the current level; the NEW column")
    print("is the rate over the windows that issue actually added.")
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if dest:
        json.dump(rows, open(dest, "w"), indent=1)
        print(f"saved {dest}")
