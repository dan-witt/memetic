#!/usr/bin/env python3
"""Fixed-window control for the churn signature — issue #4's watch item #4.

The published day-window cells (core_n, core_dominance_pct, stability_ratio, permeability_pct)
are computed over the WHOLE corpus span, which grows every issue. `weather_permeability_control.py`
controls permeability by fixing the per-cohort horizon; that construction does not extend to
core_n, dominance or stability, which are corpus-level rather than cohort-level. This control
fixes the OBSERVATION SPAN instead: recompute the identical signature over only the last N
complete calendar days before each issue's cutoff, so every issue's cell sees the same amount of
time and the series is comparable issue-to-issue.

Read the two controls as answering different questions: the cohort control asks "do arrivals
convert at a constant rate?", this one asks "does the community look the same through a
fixed-width lens?". A published series that moves while both controls stay flat is an artefact.

THE INCUMBENT-ONLY VARIANT (added at issue #10, answering issue #9's watch item #4). Fixing the
span does NOT fix the population: a day of arrivals lands inside the span and dilutes a
concentration measure mechanically, with no change in anyone's behaviour. Issue #9 saw a 71-author
influx move controlled dominance ~4 points; issue #10's 258-author influx moved it 27.7 points at
5 days. So the fixed-span cell as published is a function of recruitment and cannot be read as
concentration across issues with different inflow. The incumbent-only rows recompute the identical
signature over ONLY the authors whose first item in the whole corpus predates the span, which
removes the dilution term. It is not a fixed panel either -- the eligible set slides with the span
-- so read it as "how concentrated are the people who were already here", not as a cohort study.

Usage: MEMETIC_WORKDIR=... python3 analysis/weather_churn_control.py [N ...]   (default 5 7)
"""
import json, sys, os, datetime as dt
from pathlib import Path
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
from weather_churn import signature_windows
import corpus_store as CS
import weather_issue_boundary as IB

_CON = CS.build_index()

D = Path("/home/dan/personal/memetic/data/posts")
# (issue tag, analysis cutoff) — the cutoff is exclusive, as everywhere in the weather pipeline.
ISSUES = [("#1", "2026-08-12"), ("#2", "2026-08-13"), ("#3", "2026-08-14"),
          ("#4", "2026-08-15"), ("#5", "2026-08-18"), ("#6", "2026-08-19"),
          ("#7", "2026-08-20"), ("#8", "2026-08-21"), ("#9", "2026-08-22"),
          ("#10", "2026-08-23"), ("#11", "2026-08-24")]
CUT = lambda s: dt.datetime(*map(int, s.split("-")), tzinfo=dt.timezone.utc).timestamp()
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def stream(cutoff, observed_at=None):
    """-> [(created_at, author)] for every in-scope item below the cutoff.

    From the observation store, so a historical row can be recomputed against what that issue
    ACTUALLY SAW (observed_at) rather than against today's corpus filtered by its cutoff. Items
    backfilled since an issue ran otherwise leak into that issue's row.
    """
    return CS.author_stream(_CON, cutoff=cutoff, observed_at=observed_at)


def windowed(cutoff, n_days, incumbents_only=False, observed_at=None):
    """The signature over the last n_days COMPLETE calendar days below the cutoff.

    incumbents_only drops every author whose FIRST in-scope item falls inside the span, so an
    influx landing in the window cannot dilute the cell. See the module docstring."""
    items = stream(cutoff, observed_at)
    if not items:
        return None
    days = sorted({DAY(t) for t, _ in items})
    keep = set(days[-n_days:]) if len(days) >= n_days else None
    if keep is None:
        return None
    span = [(DAY(t), a) for t, a in items if DAY(t) in keep]
    if incumbents_only:
        first = {}
        for t, a in items:
            if a not in first or t < first[a]:
                first[a] = t
        start = min(t for t, _ in items if DAY(t) in keep)
        span = [(d, a) for d, a in span if first[a] < start]
        if not span:
            return None
    return signature_windows(span), sorted(keep)


if __name__ == "__main__":
    spans = [int(x) for x in sys.argv[1:]] or [5, 7]
    emit = {}
    for n in spans:
        for inc in (False, True):
            key = f"{n}d_incumbent_only" if inc else f"{n}d"
            label = ("last %d complete calendar days before each cutoff%s"
                     % (n, ", INCUMBENTS ONLY (author's first item predates the span)" if inc else ""))
            print(f"\n=== fixed observation span: {label} ===")
            print(f"{'issue':6s} {'span':13s} {'core_n':>7s} {'dominance%':>11s} {'stability':>10s} {'permeab%':>9s}")
            for tag, cut in ISSUES:
                r = windowed(CUT(cut), n, incumbents_only=inc,
                             observed_at=IB.issue_observed_at_for_cutoff(cut))
                if not r:
                    print(f"{tag:6s} (span does not fit below cutoff)"); continue
                sig, days = r
                emit.setdefault(key, {})[tag] = {"span": f"{days[0]}..{days[-1]}",
                    "core_n": sig["core_n"], "dominance_pct": sig["core_dominance_pct"],
                    "stability_ratio": sig["stability_ratio"], "permeability_pct": sig["permeability_pct"]}
                print(f"{tag:6s} {days[0]}..{days[-1]:6s} {sig['core_n']:>7d} {sig['core_dominance_pct']:>11.1f} "
                      f"{str(sig['stability_ratio']):>10s} {str(sig['permeability_pct']):>9s}")
    print("\nA metric that moves in the PUBLISHED series but is flat here was reading observation")
    print("length, not behaviour. A metric that moves in both is a candidate reading.")
    out = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "weather_churn_control_out.json"
    out.write_text(json.dumps(emit, indent=1))
    print(f"saved {out}")
