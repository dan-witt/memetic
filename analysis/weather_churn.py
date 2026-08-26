#!/usr/bin/env python3
"""The churn signature, shared by the weather CPU stage and its fixed-window control.

Extracted so the control cannot drift from the published metric: both import this function, so a
change to the threshold or the Jaccard construction moves the series and its control together.

THE CONFOUND THIS EXISTS FOR: "core" means active on >=3 distinct windows over however long the
corpus happens to span. Each issue adds a day, so every existing author gets another chance to
clear the bar AND another cohort joins the average -- the series can climb with no behavioural
change. Issue #4 found ~40% of the reported permeability rise was exactly that. Feed this
function a FIXED trailing span (see weather_churn_control.py) and the opportunity is constant.
"""
from collections import defaultdict, Counter
import numpy as np


def signature_windows(win_of_item, k=3):
    """generic churn signature over arbitrary window labels per item-author stream

    k is the core threshold (active in >= k windows). It is 3 everywhere the series publishes,
    and is a parameter only so a caller can measure how much a cell depends on where that step
    sits -- see weather_churn_control's core_threshold_sensitivity.
    """
    info = defaultdict(set)
    counts = Counter()
    for w, a in win_of_item:
        info[a].add(w); counts[a] += 1
    wins = sorted({w for ws in info.values() for w in ws})
    core = {a for a, ws in info.items() if len(ws) >= k}
    dom = 100 * sum(counts[a] for a in core) / sum(counts.values())
    def act(pop, w): return {a for a in pop if w in info[a]}
    def jac(pop):
        js = [len(act(pop, w1) & act(pop, w2)) / max(len(act(pop, w1) | act(pop, w2)), 1)
              for w1, w2 in zip(wins[:-1], wins[1:])]
        return float(np.mean(js)) if js else 0.0
    jc, jp = jac(core), jac(set(info))
    byc = defaultdict(list)
    firstw = {a: min(ws) for a, ws in info.items()}
    for a in info: byc[firstw[a]].append(a in core)
    cut = wins[-3] if len(wins) >= 3 else wins[-1]
    conv = [np.mean(byc[w]) for w in sorted(byc) if w <= cut and len(byc[w]) >= 10]
    return {"core_n": len(core), "core_dominance_pct": round(dom, 1),
            "stability_ratio": round(jc / jp, 2) if jp else None,
            "permeability_pct": round(100 * float(np.mean(conv)), 1) if conv else None,
            # denominators, so a move in core_n or dominance can be read against the population
            # it is a share of rather than on its own (issue #13)
            "active_n": len(info), "items": sum(counts.values()),
            "core_items": sum(counts[a] for a in core)}

# calendar-day signature (series continuity with issue #1)
