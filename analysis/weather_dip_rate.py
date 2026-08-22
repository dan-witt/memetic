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
import json, sys
from pathlib import Path

W = Path("/home/dan/personal/memetic/results/weather")
ISSUES = [("#1", "2026-08-11"), ("#2", "2026-08-12"), ("#3", "2026-08-13"),
          ("#4", "2026-08-14"), ("#5", "2026-08-17"), ("#6", "2026-08-18"),
          ("#7", "2026-08-19"), ("#8", "2026-08-20")]


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


if __name__ == "__main__":
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
