#!/usr/bin/env python3
"""Split a day's venue share into newcomers vs incumbents.

Issue #9 saw the largest author influx since the founding week (71 new authors on 08-21, after two
days at 5) and the series' lowest venue share (0.4265) on the SAME day. The obvious reader question
is whether those are one fact or two, and it is answerable from data already in hand rather than
asserted either way: every item already carries an allocation label and an author, and first
appearance is computable over the whole stream.

This is a DECOMPOSITION, not a causal claim. It says how much of a day's venue share is accounted
for by who was posting; it cannot say why newcomers allocate differently, and a day is one day.

Null: the newcomer/incumbent difference under random reassignment of the day's items to the two
groups at the observed group sizes. That holds the day's overall share and both group sizes fixed,
so it asks only whether the split by arrival cohort carries information.

Usage: MEMETIC_WORKDIR=... WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_alloc_by_cohort.py [DAY ...]
       DAY as MM-DD; defaults to the issue's final in-scope day.
"""
import json, os, sys, datetime as dt
from pathlib import Path
import numpy as np

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import weather_alloc_parse as AP

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
_c = os.environ["WEATHER_CUTOFF"]
CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
D = Path("/home/dan/personal/memetic/data/posts")


def load(d=D, cutoff=None):
    cutoff = CUTOFF if cutoff is None else cutoff
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t / 1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]),
                      ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(),
                      p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc / 1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20 and t < cutoff]


def labels(NEW, parse="strict"):
    """-> per-item 'V'/'W'/None. parse='strict' is the series currency; 'corrected' adds the
    observed WORLD phrasings back via the stored raw answers.

    Both are returned to callers separately rather than mixed: issue #9's cold review caught a
    counterfactual that paired a corrected-parse incumbent share against a strict-parse day value,
    which inflated the apparent compositional contribution about fourfold.
    """
    lc = json.load(open(S / "allocation_label_cache_agent.json"))
    rawf = S / "allocation_unparsed_raw_agent.json"
    raw = json.load(open(rawf)) if rawf.exists() else {}
    out = []
    for t, k, x, a in NEW:
        kk = f"{k[0]}:{k[1]}"
        l = lc.get(kk)
        if l is None and parse == "corrected" and kk in raw:
            l = AP.corrected(raw[kk])
        out.append(l)
    return out


def decompose(day, NEW=None, lab=None, draws=20000, seed=20260822, parse="strict"):
    NEW = load() if NEW is None else NEW
    lab = labels(NEW, parse) if lab is None else lab
    first = {}
    for t, k, x, a in NEW:
        if a not in first: first[a] = t
    # year from the data, not hardcoded
    _yr = dt.datetime.fromtimestamp(max(t for t, k, x, a in NEW), dt.timezone.utc).year
    day_start = dt.datetime.strptime(
        f"{_yr}-{day}", "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp()
    rows = [(lab[i] == "V", first[NEW[i][3]] >= day_start)
            for i, (t, k, x, a) in enumerate(NEW) if DAY(t) == day and lab[i]]
    if not rows: return None
    v = np.array([r[0] for r in rows], float)
    isnew = np.array([r[1] for r in rows], bool)
    n_new, n_inc = int(isnew.sum()), int((~isnew).sum())
    if n_new == 0 or n_inc == 0: return None
    s_new, s_inc = float(v[isnew].mean()), float(v[~isnew].mean())
    obs = s_new - s_inc
    rng = np.random.default_rng(seed)
    nulls = np.array([(lambda q: v[q[:n_new]].mean() - v[q[n_new:]].mean())(rng.permutation(len(v)))
                      for _ in range(draws)])
    p = float((np.abs(nulls) >= abs(obs) - 1e-12).mean())
    # counterfactual: the day's share if newcomers had allocated like incumbents
    cf = s_inc
    return {"day": day, "parse": parse, "n_labelled": len(rows),
            "newcomer_items": n_new, "incumbent_items": n_inc,
            "venue_share_day": round(float(v.mean()), 4),
            "venue_share_newcomers": round(s_new, 4),
            "venue_share_incumbents": round(s_inc, 4),
            "difference": round(obs, 4),
            "p_two_sided_permutation": round(p, 4), "draws": draws,
            "day_share_if_newcomers_allocated_like_incumbents": round(cf, 4),
            # The incumbent-only share became a published SERIES at issue #10, so it needs the same
            # noise scale the report demands of every other single-day cell. Binomial counting
            # noise only, on the group's own labelled count; classifier error is not in it.
            "counting_se_incumbents": round((s_inc * (1 - s_inc) / n_inc) ** 0.5, 4),
            "counting_se_newcomers": round((s_new * (1 - s_new) / n_new) ** 0.5, 4),
            "note": "decomposition, not a causal claim; one day; newcomer = author's first item in "
                    "the whole stream falls on this day. The test has power only for large "
                    "differences, so a non-significant result licenses 'the difference does not run "
                    "the way the compositional story needs', not 'the groups are identical'.",
            }


if __name__ == "__main__":
    NEW = load()
    days = sys.argv[1:] or [DAY(max(t for t, k, x, a in NEW))]
    out = {}
    for parse in ("strict", "corrected"):
        lab = labels(NEW, parse)
        for d in days:
            r = decompose(d, NEW, lab, parse=parse)
            if not r:
                print(f"{d} [{parse}]: not decomposable"); continue
            out.setdefault(d, {})[parse] = r
            print(f"{d} [{parse}]: day {r['venue_share_day']:.4f} = newcomers "
                  f"{r['venue_share_newcomers']:.4f} (n={r['newcomer_items']}) vs incumbents "
                  f"{r['venue_share_incumbents']:.4f} (n={r['incumbent_items']});  "
                  f"diff {r['difference']:+.4f}, p={r['p_two_sided_permutation']:.4f}")
            print(f"     day's share had newcomers allocated like incumbents: "
                  f"{r['day_share_if_newcomers_allocated_like_incumbents']:.4f} "
                  f"(actual {r['venue_share_day']:.4f}, same parse)")
    dest = S / "weather_alloc_by_cohort_out.json"
    dest.write_text(json.dumps(out, indent=1)); print("saved", dest)
