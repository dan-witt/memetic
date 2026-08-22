#!/usr/bin/env python3
"""The significance arithmetic the weather report cites, in one runnable place.

Two small tests kept turning up as inline arithmetic in the prose, which is exactly the pattern
the review gate exists to stop: a number in the report that no script produces. Both are here,
both read the PUBLISHED results.json so they cannot drift from what shipped, and both are
deliberately conservative about what they license.

  sign_tail   - "four of the last five daily moves were negative; so what?" The one-sided
                binomial tail P(X >= k) under fair-coin signs. This is an UPPER bound on how
                impressive a run is, because daily moves on these series are autocorrelated and
                autocorrelation makes runs cheaper, not dearer. A tail that fails to reach
                significance under the generous assumption fails under the real one too, which is
                the only direction this test is used in.

  run_below   - "three consecutive days below the comparator's lower bound fired a pre-registered
                rule; was the CLUSTERING itself surprising?" Exact permutation over day order,
                holding the observed multiset of daily values fixed. It asks one narrow question:
                given that k of n days fell below the threshold, how often would they land in a
                run this long if the order were random? It does NOT test whether the level moved
                -- exchangeability is the wrong null for a series with drift, since a drifting
                series puts its lowest values adjacent for free. Cited only alongside that caveat.

  fisher_2x2  - two-sided Fisher exact for a change in a count-out-of-n rate between two issues
                (used for the sub-forth dip rate). The rolling windows OVERLAP - 120 items
                advancing by 40 - so the nominal n of 19 windows carries roughly 6-7 independent
                observations, and Fisher on the nominal n is ANTI-conservative. Again used in one
                direction only: when even the anti-conservative test fails to reach significance,
                "not distinguishable" is safe.

Usage: python3 analysis/weather_trend_tests.py [issue-date]   (default: newest published issue)
"""
import json, sys
from math import comb
from pathlib import Path

W = Path("/home/dan/personal/memetic/results/weather")


def sign_tail(k, n):
    """-> P(X >= k) for X ~ Binomial(n, 1/2). One-sided; see the caveat above."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def fisher_2x2(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]], by summing tables no more likely than the
    observed one (the conventional two-sided definition, not a doubled one-sided tail)."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    def prob(x):
        y, z, w = r1 - x, c1 - x, r2 - (c1 - x)
        if min(y, z, w) < 0: return 0.0
        return comb(r1, x) * comb(r2, z) / comb(n, c1)
    obs = prob(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return sum(p for x in range(lo, hi + 1) if (p := prob(x)) <= obs + 1e-15)


def longest_run(mask):
    """-> length of the longest run of True in `mask`."""
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return best


def run_below(values, thresh):
    """Exact permutation test on the CLUSTERING of sub-threshold days. See the caveat above.

    Enumerates every way k below-threshold days could be arranged among n days (all orders
    equally likely) and returns the share whose longest run is at least the observed one. Exact
    when C(n, k) is enumerable, which it is at these series lengths.
    """
    from itertools import combinations
    n = len(values)
    below = [i for i, v in enumerate(values) if v < thresh]
    k = len(below)
    obs = longest_run([v < thresh for v in values])
    if k == 0 or k == n:
        return {"n_days": n, "k_below": k, "threshold": thresh, "longest_run": obs, "p_exact": None,
                "read": "degenerate: every day on one side of the threshold"}
    total = hit = 0
    for c in combinations(range(n), k):
        m = [False] * n
        for i in c: m[i] = True
        total += 1
        if longest_run(m) >= obs: hit += 1
    return {"n_days": n, "k_below": k, "threshold": thresh, "longest_run": obs,
            "arrangements": total, "at_least_as_clustered": hit,
            "p_exact": round(hit / total, 4),
            "read": "tests CLUSTERING under random day order, not a level shift. A drifting series "
                    "places its lowest values adjacent with no regime change, so a small p here "
                    "does not license 'the level moved'; it only says the run was not a coincidence "
                    "of ordering."}


def trailing_means(values, days, k=5):
    """-> the trailing k-day mean of the series at every day it is defined.

    Issue #8's replacement for issue #5's "k consecutive days below the bound" rule. A run of
    single days below a threshold is satisfiable by an excursion that reverses -- which is what
    issues #7 and #8 observed -- so it tests clustering, not level. A trailing mean has to stay
    down to fire, which is what "the level moved" actually means.
    """
    out = {}
    for i in range(k - 1, len(values)):
        out[days[i]] = round(sum(values[i - k + 1:i + 1]) / k, 4)
    return out


def report(issue_date):
    d = json.load(open(W / issue_date / "results.json"))
    out = {"issue": d["issue"]}

    # (1) allocation: sign count over the daily moves since the excursion's run-up began.
    alloc = d["allocation_trend"]["venue_share_per_day_qwen_binary"]
    days = sorted(alloc)
    tail5 = days[-6:]                      # 6 levels -> 5 moves
    moves = [round(alloc[b] - alloc[a], 4) for a, b in zip(tail5[:-1], tail5[1:])]
    neg = sum(1 for m in moves if m < 0)
    out["allocation_sign_test"] = {
        "days": tail5, "moves": moves, "negative": neg, "n": len(moves),
        "p_one_sided_fair_coin": round(sign_tail(neg, len(moves)), 4),
        "read": "upper bound on how surprising the run is; autocorrelation makes runs cheaper, so "
                "failing to reach significance here fails a fortiori. Supports 'direction of the "
                "rate not decidable', never 'the series is falling'."}

    # (2) the three-day below-platform run: was the clustering itself surprising?
    # Threshold = the frozen comparator's own CI95 lower bound, read from the baseline artifact
    # (not retyped here) so the test and the reading cannot drift apart.
    _lo = json.load(open(Path("/home/dan/personal/memetic/results/lemmy_baseline/results.json"))
                    )["allocation"]["all_items"]["qwen"]["share_lemmy_all"]["ci95"][0]
    out["below_platform_run"] = dict(run_below([alloc[k] for k in days], _lo),
                                     series="strict", days=days,
                                     threshold_source="lemmy_baseline share_lemmy_all ci95 lower")

    # (3) the proposed replacement rule: does the LEVEL stay down, not just single days?
    _vals = [alloc[k] for k in days]
    _tm = trailing_means(_vals, days, 5)
    _below = [d for d, v in _tm.items() if v < _lo]
    # The read string is DERIVED, not carried: issue #9's cold review found the previous fixed
    # string still asserting "never went below the bound" in the same JSON block as a non-empty
    # days_below_threshold. A machine-readable record must not contradict its own field.
    if not _below:
        _read = ("issue #8's level-shift rule. This statistic has never gone below the bound, so it "
                 "would not have produced the issue #5 rule's false positive.")
    else:
        _read = (f"issue #8's level-shift rule, and it HAS crossed: {len(_below)} day(s) below the "
                 f"bound ({', '.join(_below)}), deepest {min(_tm.values()):.4f} against {_lo}. "
                 "Issue #8's condition was 'goes below AND stays', so a single crossing is half of "
                 "it. Read the crossing DEPTH against the statistic's own counting noise before "
                 "treating it as a level change.")
    out["trailing_5day_mean"] = {"series": _tm, "threshold": _lo,
                                 "days_below_threshold": _below, "read": _read}

    # (4) dip rate: this issue's new-window dip count against the previous issue's.
    rows = d["idea_time_series"]["per_issue_dip_rate"]
    if len(rows) >= 2:
        cur, prv = rows[-1], rows[-2]
        a, b = cur["new_below_forth"], cur["new_windows"] - cur["new_below_forth"]
        c, e = prv["new_below_forth"], prv["new_windows"] - prv["new_below_forth"]
        out["dip_rate_change"] = {
            "issue": cur["issue"], "prev_issue": prv["issue"],
            "counts": f"{a}/{cur['new_windows']} vs {c}/{prv['new_windows']}",
            "pct": [cur["new_below_forth_pct"], prv["new_below_forth_pct"]],
            "p_two_sided_fisher": round(fisher_2x2(a, b, c, e), 4),
            "effective_independent_windows_each": "~6-7 (120-item windows advancing by 40)",
            "read": "anti-conservative on the nominal n; a non-significant result here is safe, a "
                    "significant one would not be."}
    return out


if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else sorted(
        q.name for q in W.glob("20*-*-*") if (q / "results.json").exists())[-1]
    print(json.dumps(report(date), indent=1))
