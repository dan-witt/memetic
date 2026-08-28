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

THE CORE THRESHOLD IS A STEP, AND THE CELL INHERITS ITS FRAGILITY (added at issue #13). "Core"
means active in >= 3 of the span's days, so an author sitting on that boundary moves ALL of their
items across the core/non-core line by being active one fewer day. Over a 5-day span a handful of
borderline authors can therefore move dominance by more than the pre-registered alert threshold
with no change in the population's size or output. `core_threshold_sensitivity` recomputes the
incumbent-only dominance at k = 2, 3 and 4: a move that appears only at the published k = 3 is a
property of where the step sits, not of concentration. Issue #13 is the case this was built for --
its -3.3 point move at k=3 reads -0.9 at k=2 and -0.4 at k=4.

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
WEATHER = Path("/home/dan/personal/memetic/results/weather")


def _issues():
    """[(issue tag, analysis cutoff)] — derived, not hand-listed.

    An issue dated D is produced with cutoff D+1, so the published directories give the whole
    table. The issue being produced has no directory yet, so WEATHER_CUTOFF appends it; that is
    also what lets this issue's own cell appear in the comparison it is written from.
    """
    dirs = sorted(q.name for q in WEATHER.glob("20*-*-*") if (q / "results.json").exists())
    cuts = [(dt.datetime.strptime(d, "%Y-%m-%d") + dt.timedelta(days=1)).strftime("%Y-%m-%d")
            for d in dirs]
    cur = os.environ.get("WEATHER_CUTOFF")
    if cur and cur not in cuts:
        cuts.append(cur)
    return [(f"#{i+1}", c) for i, c in enumerate(cuts)]


# (issue tag, analysis cutoff) — the cutoff is exclusive, as everywhere in the weather pipeline.
ISSUES = _issues()
CUT = lambda s: dt.datetime(*map(int, s.split("-")), tzinfo=dt.timezone.utc).timestamp()
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def stream(cutoff, observed_at=None):
    """-> [(created_at, author)] for every in-scope item below the cutoff.

    From the observation store, so a historical row can be recomputed against what that issue
    ACTUALLY SAW (observed_at) rather than against today's corpus filtered by its cutoff. Items
    backfilled since an issue ran otherwise leak into that issue's row.
    """
    return CS.author_stream(_CON, cutoff=cutoff, observed_at=observed_at)


def windowed(cutoff, n_days, incumbents_only=False, observed_at=None, k=3):
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
    return signature_windows(span, k=k), sorted(keep)


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
                    "stability_ratio": sig["stability_ratio"], "permeability_pct": sig["permeability_pct"],
                    "active_n": sig["active_n"], "items": sig["items"], "core_items": sig["core_items"]}
                print(f"{tag:6s} {days[0]}..{days[-1]:6s} {sig['core_n']:>7d} {sig['core_dominance_pct']:>11.1f} "
                      f"{str(sig['stability_ratio']):>10s} {str(sig['permeability_pct']):>9s}")
    # Core-threshold sensitivity for the incumbent-only rows. The published cell is k=3; the
    # neighbours exist so a move can be attributed to concentration or to the step's placement.
    for n in spans:
        key = f"{n}d_incumbent_only_core_threshold_sensitivity"
        print(f"\n=== core-threshold sensitivity, {n}-day incumbent-only dominance% (published cell is k=3) ===")
        print(f"{'issue':6s} {'span':13s} " + " ".join(f"{'k=' + str(k):>14s}" for k in (2, 3, 4)))
        for tag, cut in ISSUES:
            cells = {}
            for k in (2, 3, 4):
                r = windowed(CUT(cut), n, incumbents_only=True,
                             observed_at=IB.issue_observed_at_for_cutoff(cut), k=k)
                if r: cells[k] = (r[0]["core_dominance_pct"], r[0]["core_n"], r[1],
                                  r[0]["active_n"], r[0]["items"], r[0]["core_items"])
            if not cells:
                print(f"{tag:6s} (span does not fit below cutoff)"); continue
            days = cells[3][2]
            emit.setdefault(key, {})[tag] = {"span": f"{days[0]}..{days[-1]}",
                **{f"k{k}_dominance_pct": cells[k][0] for k in cells},
                **{f"k{k}_core_n": cells[k][1] for k in cells},
                "active_n": cells[3][3], "items": cells[3][4], "k3_core_items": cells[3][5]}
            print(f"{tag:6s} {days[0]}..{days[-1]:6s} " +
                  " ".join(f"{cells[k][0]:7.1f} (n={cells[k][1]:3d})" for k in (2, 3, 4)))
        print("   a move visible only at k=3 is the step's placement, not concentration.")

    print("\nA metric that moves in the PUBLISHED series but is flat here was reading observation")
    print("length, not behaviour. A metric that moves in both is a candidate reading.")
    out = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "weather_churn_control_out.json"
    out.write_text(json.dumps(emit, indent=1))
    print(f"saved {out}")
