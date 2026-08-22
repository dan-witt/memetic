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
import json, os, datetime as dt
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

def fixed_horizon_rows(ev, N):
    """-> {cohort day: [converted bool per author]} at horizon N. Author-level, unfiltered."""
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
    return byc


MIN_N = 10   # cohort-size floor for the DISPLAYED per-cohort cells; see MIN_N_TREND below.
# Issue #7 found this floor was undisclosed and load-bearing: with inflow at 5-8 authors a day no
# future cohort reaches 10, so the pre-registered primary horizon could never update again, and
# re-reporting a frozen statistic as a fresh measurement is what two other cells were retired for.
# Issue #8's decision (watch item #7): the floor stays at 10 for the displayed per-cohort table,
# where a percentage over six authors is noise, and drops to 5 for the TREND test, which is
# author-level and permutation-nulled and so does not need per-cohort estimates to be stable.
# Sunset: if inflow makes even n>=5 cohorts unavailable, the test retires rather than being
# re-reported frozen.
MIN_N_TREND = 5

def fixed_horizon_permeability(ev, N, min_n=MIN_N):
    """>=3 active days within the cohort's first N CALENDAR days (arrival day inclusive).
    Only cohorts whose full N-day window fits below the cutoff, and that clear `min_n`, count."""
    byc = fixed_horizon_rows(ev, N)
    conv = {w: (round(100 * float(np.mean(v)), 1), len(v)) for w, v in sorted(byc.items()) if len(v) >= min_n}
    overall = round(100 * float(np.mean([np.mean(byc[w]) for w in sorted(byc) if len(byc[w]) >= min_n])), 1) if conv else None
    return overall, conv


def cohort_trend(ev, N, draws=20000, seed=20260819, min_n=MIN_N):
    """Author-level test of 'do LATER arrival cohorts convert better?' at horizon N.

    The per-issue running mean cannot answer this — a cohort's cell is frozen once its window
    closes, so that series moves only by composition. The object that carries behaviour is the
    per-cohort sequence itself. Statistic: point-biserial correlation between an author's cohort
    INDEX (rank of arrival day among qualifying cohorts, equally spaced) and whether they
    converted. Null by permuting the conversion labels across all authors, which holds the
    per-cohort n and the overall conversion rate fixed. Two-sided.
    """
    byc = fixed_horizon_rows(ev, N)
    days = [w for w in sorted(byc) if len(byc[w]) >= min_n]
    if len(days) < 3: return None
    idx = np.concatenate([np.full(len(byc[w]), i, float) for i, w in enumerate(days)])
    y = np.concatenate([np.array(byc[w], float) for w in days])
    def r(v):
        sx, sy = idx.std(), v.std()
        return 0.0 if sx == 0 or sy == 0 else float(((idx - idx.mean()) * (v - v.mean())).mean() / (sx * sy))
    obs = r(y)
    rng = np.random.default_rng(seed)
    null = np.array([r(rng.permutation(y)) for _ in range(draws)])
    p = float((np.abs(null) >= abs(obs) - 1e-12).mean())
    return {"n_authors": int(len(y)), "n_cohorts": len(days), "min_n": min_n, "r": round(obs, 4),
            "p_perm": round(p, 4), "draws": draws,
            "per_cohort": [(w, round(100 * float(np.mean(byc[w])), 1), len(byc[w])) for w in days]}

# cutoff = each issue's analysis cutoff; last_item = the last item that issue's pull actually had
# (issue #1's pull ran mid-day on 08-11, so its final day was partial — its cell is not on the
# same footing as #2-#4 and only reproduces against that truncation, not against a complete 08-11)
ISSUES = [("#1", "2026-08-12", 30.5, "2026-08-11T19:56:47Z"), ("#2", "2026-08-13", 33.6, None),
          ("#3", "2026-08-14", 35.5, None), ("#4", "2026-08-15", 39.4, None),
          ("#5", "2026-08-18", 42.9, None), ("#6", "2026-08-19", 43.9, None),
          ("#7", "2026-08-20", 46.9, None), ("#8", "2026-08-21", 47.2, None),
          ("#9", "2026-08-22", 48.2, None)]
D = "/home/dan/personal/memetic/data/posts"
EMIT = {"fixed_horizon": {}, "membership_held_fixed": {}, "cohort_trend": {}}
print(f"{'issue':6s} {'cutoff':12s} {'published':>10s} {'reproduced':>11s}  {'N=3':>6s} {'N=4':>6s} {'N=5':>6s}")
for tag, cut, pub, trunc in ISSUES:
    ev = load(D, CUT(cut))
    if trunc:   # reproduce against the data that issue actually held
        lim = dt.datetime.strptime(trunc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
        rep = published_permeability([(t, a) for t, a in ev if t <= lim])[0]
    else:
        rep = published_permeability(ev)[0]
    ns = [fixed_horizon_permeability(ev, n)[0] for n in (3, 4, 5)]
    EMIT["fixed_horizon"][tag] = {"cutoff": cut, "published": pub, "reproduced": rep,
                                  "N3": ns[0], "N4": ns[1], "N5": ns[2]}
    print(f"{tag:6s} {cut:12s} {pub:10.1f} {rep:11.1f}  " + " ".join(f"{str(x):>6s}" for x in ns))
print("  (issue #1 'reproduced' is against its own partial-day truncation; with a complete 08-11")
print("   the same metric reads 32.2 — a different measurement, not data drift)")

# Per-cohort conversion is a property of the cohort's own fixed window, so a given cohort's cell
# does NOT change as the cutoff advances; what changes is WHICH cohorts qualify (a cohort enters a
# horizon only once its full N-day window sits below the cutoff). Printing the newest issue's block
# alongside the previous issue's cohort SET is what separates a behavioural move from an entry.
NEWEST, PREV = ISSUES[-1], ISSUES[-2]
print(f"\nper-cohort conversion at each horizon, issue {NEWEST[0]} — cohort: (pct, n)")
ev = load(D, CUT(NEWEST[1]))
ev_prev = load(D, CUT(PREV[1]))
for n in (3, 4, 5):
    _, c = fixed_horizon_permeability(ev, n)
    _, cp = fixed_horizon_permeability(ev_prev, n)
    entered = [k for k in c if k not in cp]
    print(f"   first {n} calendar days: " + ", ".join(f"{k} {v[0]}% (n={v[1]})" for k, v in c.items()))
    print(f"      cohorts new since {PREV[0]}: {entered if entered else 'none — like-for-like'}")

# Membership decomposition: the fixed-horizon cell is an unweighted mean over qualifying cohorts,
# so it can move for two reasons — cohorts converting differently, or a new cohort entering the
# mean. Recomputing over the INTERSECTION of the two issues' cohort sets holds membership fixed
# and isolates the behavioural part. (Issue #5's watch item #3 asked for exactly this view.)
print(f"\nmembership-held-fixed: {NEWEST[0]} recomputed over only the cohorts {PREV[0]} also had")
for n in (3, 4, 5):
    _, c = fixed_horizon_permeability(ev, n)
    _, cp = fixed_horizon_permeability(ev_prev, n)
    shared = [k for k in c if k in cp]
    entered_n = [k for k in c if k not in cp]   # per-horizon; NOT the loop above's `entered`
    held = round(float(np.mean([c[k][0] for k in shared])), 1)
    prev = round(float(np.mean([cp[k][0] for k in shared])), 1)
    full = round(float(np.mean([v[0] for v in c.values()])), 1)
    print(f"   N={n}: {PREV[0]} {prev} -> {NEWEST[0]} {held} on the shared {len(shared)} cohorts"
          f"   (all-cohort {NEWEST[0]} cell: {full}; gap = entry, not behaviour)")
    # Strict check, not decoration: a cohort's window is frozen once it closes, so a shared
    # cohort's cell MUST be bit-identical across issues. A mismatch means the past moved
    # (backfill or an edit adding an author to a closed day) and the series needs a rebuild.
    drift = {k: (cp[k], c[k]) for k in shared if cp[k] != c[k]}
    EMIT["membership_held_fixed"][f"N{n}"] = {"prev_issue": PREV[0], "issue": NEWEST[0],
        "shared_cohorts": len(shared), "prev_on_shared": prev, "issue_on_shared": held,
        "issue_all_cohorts": full, "entered": entered_n,
        "per_cohort_identity": "HOLDS" if not drift else "VIOLATED", "drift": drift}
    print(f"      per-cohort identity across the boundary: "
          + ("HOLDS" if not drift else f"VIOLATED {drift}"))

# The replacement reported object. Since the running mean moves only by composition, the
# question "is the community getting more permeable?" has to be asked of the per-cohort sequence.
print(f"\nper-cohort conversion TREND (author-level, permutation null) at issue {NEWEST[0]}'s cutoff")
for label, mn in (("n>=10 (issues #6-#7 currency, frozen)", MIN_N),
                  ("n>=5 (issue #8 primary)", MIN_N_TREND)):
    print(f"   cohort floor {label}")
    for n in (3, 4, 5):
        tr = cohort_trend(ev, n, min_n=mn)
        if not tr: continue
        EMIT["cohort_trend"][f"N{n}_minn{mn}"] = tr
        if mn == MIN_N: EMIT["cohort_trend"][f"N{n}"] = tr   # back-compat key for issues #6-#7
        print(f"      N={n}: r={tr['r']:+.4f}  p={tr['p_perm']:.4f}  "
              f"({tr['n_authors']} authors over {tr['n_cohorts']} cohorts, {tr['draws']} draws)")
        print("           " + ", ".join(f"{w} {v}% (n={m})" for w, v, m in tr["per_cohort"]))

print("\ncohorts entering the PUBLISHED average, by issue (the average's membership changes):")
for tag, cut, pub, trunc in ISSUES:
    _, cohorts = published_permeability(load(D, CUT(cut)))
    print(f"   {tag}: {cohorts}")

out = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "weather_permeability_control_out.json"
out.write_text(json.dumps(EMIT, indent=1))
print(f"\nsaved {out}")
