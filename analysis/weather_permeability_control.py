#!/usr/bin/env python3
"""Is the rising day-window permeability real, or an artefact of observation length?

The published metric counts an author as 'core' if active on >=3 distinct calendar days,
over however many days the corpus happens to span. Each new issue grants every existing
cohort one more day to clear that bar, so the series can rise with no behavioural change.

Control: FIXED-HORIZON permeability — for each cohort day d, the fraction of authors first seen
on d who were active on >=3 distinct days within the cohort's first N CALENDAR days (the arrival
day inclusive, i.e. d .. d+N-1), counted only for cohorts whose full N-day window fits below the
cutoff. Same threshold, same data, constant opportunity.

NOTE ON LABELS: horizons here are stated as CALENDAR-DAY SPANS INCLUSIVE OF THE ARRIVAL DAY.
N=3 means "3 active days out of the arrival day and the two that follow" — which, with a >=3
threshold, means active on every one of them. An earlier draft of this control labelled these
spans H=3/H=4 while computing 4 and 5 calendar days; the numbers were right, the labels off by
one. Read N as a span, not as "days after arrival".
"""
import json, datetime as dt
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

def load(d, cutoff):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort()
    return [(t, a) for t, x, a in items if len(x) >= 20 and t < cutoff]

DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
CUT = lambda s: dt.datetime(*map(int, s.split("-")), tzinfo=dt.timezone.utc).timestamp()

def published_permeability(ev):
    """the metric as shipped: core = active on >=3 days over the WHOLE corpus span"""
    info = defaultdict(set)
    for t, a in ev: info[a].add(DAY(t))
    wins = sorted({w for ws in info.values() for w in ws})
    core = {a for a, ws in info.items() if len(ws) >= 3}
    firstw = {a: min(ws) for a, ws in info.items()}
    byc = defaultdict(list)
    for a in info: byc[firstw[a]].append(a in core)
    cut = wins[-3] if len(wins) >= 3 else wins[-1]
    conv = [np.mean(byc[w]) for w in sorted(byc) if w <= cut and len(byc[w]) >= 10]
    return round(100 * float(np.mean(conv)), 1), [w for w in sorted(byc) if w <= cut and len(byc[w]) >= 10]

def fixed_horizon_permeability(ev, N):
    """>=3 active days within the cohort's first N CALENDAR days (arrival day inclusive).
    Only cohorts whose full N-day window fits below the cutoff are counted."""
    info = defaultdict(set)
    for t, a in ev: info[a].add(DAY(t))
    wins = sorted({w for ws in info.values() for w in ws})
    firstw = {a: min(ws) for a, ws in info.items()}
    byc = defaultdict(list)
    for a, ws in info.items():
        d0 = firstw[a]
        i0 = wins.index(d0)
        if i0 + N - 1 >= len(wins):   # incomplete horizon -> cohort excluded entirely
            continue
        byc[d0].append(len(ws & set(wins[i0:i0 + N])) >= 3)
    conv = {w: (round(100 * float(np.mean(v)), 1), len(v)) for w, v in sorted(byc.items()) if len(v) >= 10}
    overall = round(100 * float(np.mean([np.mean(byc[w]) for w in sorted(byc) if len(byc[w]) >= 10])), 1) if conv else None
    return overall, conv

# cutoff = each issue's analysis cutoff; last_item = the last item that issue's pull actually had
# (issue #1's pull ran mid-day on 08-11, so its final day was partial — its cell is not on the
# same footing as #2-#4 and only reproduces against that truncation, not against a complete 08-11)
ISSUES = [("#1", "2026-08-12", 30.5, "2026-08-11T19:56:47Z"), ("#2", "2026-08-13", 33.6, None),
          ("#3", "2026-08-14", 35.5, None), ("#4", "2026-08-15", 39.4, None),
          ("#5", "2026-08-18", 42.9, None)]
D = "/home/dan/personal/memetic/data/posts"
print(f"{'issue':6s} {'cutoff':12s} {'published':>10s} {'reproduced':>11s}  {'N=3':>6s} {'N=4':>6s} {'N=5':>6s}")
for tag, cut, pub, trunc in ISSUES:
    ev = load(D, CUT(cut))
    if trunc:   # reproduce against the data that issue actually held
        lim = dt.datetime.strptime(trunc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
        rep = published_permeability([(t, a) for t, a in ev if t <= lim])[0]
    else:
        rep = published_permeability(ev)[0]
    ns = [fixed_horizon_permeability(ev, n)[0] for n in (3, 4, 5)]
    print(f"{tag:6s} {cut:12s} {pub:10.1f} {rep:11.1f}  " + " ".join(f"{str(x):>6s}" for x in ns))
print("  (issue #1 'reproduced' is against its own partial-day truncation; with a complete 08-11")
print("   the same metric reads 32.2 — a different measurement, not data drift)")

print("\nper-cohort conversion at each horizon, issue #4 — cohort: (pct, n)")
ev = load(D, CUT("2026-08-15"))
for n in (3, 4, 5):
    _, c = fixed_horizon_permeability(ev, n)
    print(f"   first {n} calendar days: " + ", ".join(f"{k} {v[0]}% (n={v[1]})" for k, v in c.items()))

print("\ncohorts entering the PUBLISHED average, by issue (the average's membership changes):")
for tag, cut, pub, trunc in ISSUES:
    _, cohorts = published_permeability(load(D, CUT(cut)))
    print(f"   {tag}: {cohorts}")
