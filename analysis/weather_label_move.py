#!/usr/bin/env python3
"""Attribute a retro-movement in the allocation series to a count of items.

weather_gpu.py's label audit reports THAT an already-published day moved (see
allocation_trend.label_audit.published_days_moved). This attributes the move: the daily venue
share is v/n with v venue-labelled items out of n labelled items, both integers, so a published
share of 0.4726 and a current share of 0.4720 pin down (v, n) exactly when the search over
plausible n admits only one solution. That turns "a label retry moved the day" into "exactly k
items gained a label and they were labelled X".

The current issue publishes n directly (label_audit.per_day[day].labelled), so only the previous
issue's pair has to be recovered. A move with more than one candidate pair is reported as
ambiguous rather than guessed at.

Usage: python3 analysis/weather_label_move.py [issue-date]      (default: newest published issue)
"""
import json, sys
from pathlib import Path

W = Path("/home/dan/personal/memetic/results/weather")


def solve(share, n_hint, span=60, vmin=0, vmax=None):
    """-> [(v, n)] with round(v/n, 4) == share, n within +-span of n_hint."""
    lo, hi = max(1, n_hint - span), n_hint + span
    out = []
    for n in range(lo, hi + 1):
        for v in range(vmin, (vmax if vmax is not None else n) + 1):
            if round(v / n, 4) == share:
                out.append((v, n))
    return out


def attribute(issue_date):
    d = json.load(open(W / issue_date / "results.json"))
    audit = d["allocation_trend"].get("label_audit") or {}
    moved = audit.get("published_days_moved") or {}
    per_day = audit.get("per_day") or {}
    rows = []
    for day, m in sorted(moved.items()):
        n_now = (per_day.get(day) or {}).get("labelled")
        if n_now is None:
            rows.append({"day": day, "status": "no per-day label count published"}); continue
        now = solve(m["this_issue"], n_now, span=0)
        then = solve(m["prev_issue"], n_now, span=15)
        r = {"day": day, "prev_share": m["prev_issue"], "this_share": m["this_issue"],
             "delta": m["delta"], "labelled_now": n_now,
             "candidates_now": now, "candidates_prev": then}
        if len(now) == 1 and len(then) == 1:
            (v1, n1), (v0, n0) = now[0], then[0]
            r["attribution"] = {
                "items_gained_a_label": n1 - n0, "venue_labels_gained": v1 - v0,
                "world_labels_gained": (n1 - n0) - (v1 - v0),
                "reads": f"{v0}/{n0} -> {v1}/{n1}"}
        else:
            r["attribution"] = "AMBIGUOUS - more than one (v, n) pair fits; not attributed"
        rows.append(r)
    return rows


if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else sorted(
        q.name for q in W.glob("20*-*-*") if (q / "results.json").exists())[-1]
    rows = attribute(date)
    print(f"issue {date}: {len(rows)} published day(s) moved")
    for r in rows:
        if "prev_share" not in r:
            print(f"  {r['day']}: {r['status']}"); continue
        print(f"  {r['day']}: {r['prev_share']} -> {r['this_share']} ({r['delta']:+})")
        a = r["attribution"]
        if isinstance(a, str):
            print(f"      {a}  candidates: prev={r['candidates_prev']} now={r['candidates_now']}")
        else:
            print(f"      {a['reads']}: {a['items_gained_a_label']} item(s) gained a label "
                  f"({a['venue_labels_gained']} VENUE, {a['world_labels_gained']} WORLD)")
    if not rows:
        print("  none - no already-published day moved this issue")
