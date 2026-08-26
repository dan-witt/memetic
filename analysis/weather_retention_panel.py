#!/usr/bin/env python3
"""Fixed-membership retention: does a day's traffic come from authors who were already here?

The daily newcomer/incumbent split cannot answer this. "Incumbent" there means "not new TODAY", so
an author who arrived yesterday is counted as an incumbent tomorrow -- the incumbent population
grows mechanically with every arrival day, and its item count grows with it. Issues #9-#12
demonstrated the same confound three times over for the concentration cells; this is the structural
version of it, and every cell below exists to avoid it.

The construction: partition authors by their ARRIVAL DAY, once, and then read each partition's
activity on each later day. Membership never changes, so a rise in a partition's item count is that
partition posting more, not the partition getting bigger.

  panel[cohort][day] = (active authors, items)

Two derived readings the report uses:

  pre_event     the population that existed before an influx began (arrival <= a stated day).
                Its trajectory answers "did the pre-existing square change?" -- a question the
                daily incumbent series cannot ask, because after one arrival day the daily
                incumbents are no longer the pre-existing square.
  retained      each event cohort's activity on the newest day, as a fraction of its size. This is
                the retention rate the series has been asking for since issue #11, and it needs no
                assumption about arrivals stopping.

A cohort's "active authors on day D" is a headcount of identities, not operators (see any issue's
caveats). Cells are descriptive; no test is attached.

Usage: WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_retention_panel.py [PRE_EVENT_LAST_DAY]
       PRE_EVENT_LAST_DAY defaults to 08-20 (the last day before the 08-21 influx began).
"""
import datetime as dt, json, os, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS

DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def panel(rows, pre_event_last):
    """-> (arrival day per author, {cohort: {day: {"authors": n, "items": n}}}).

    `rows` is [(created_at, author)] over the whole in-scope corpus; arrival is the first item in
    that stream, so the partition is fixed by construction and independent of the day being read.
    """
    arrival, by_day = {}, defaultdict(lambda: defaultdict(set))
    items = defaultdict(lambda: defaultdict(int))
    for t, a in sorted(rows):
        arrival.setdefault(a, DAY(t))
    for t, a in rows:
        c = arrival[a]
        by_day[c][DAY(t)].add(a)
        items[c][DAY(t)] += 1
    out = {}
    for c in sorted(by_day):
        out[c] = {d: {"authors": len(by_day[c][d]), "items": items[c][d]}
                  for d in sorted(by_day[c])}
    # the pre-event partition is a UNION of cohorts, formed once and then read like any other
    pre = [c for c in out if c <= pre_event_last]
    merged = defaultdict(lambda: {"authors": 0, "items": 0})
    for c in pre:
        for d, v in out[c].items():
            merged[d]["authors"] += v["authors"]; merged[d]["items"] += v["items"]
    return arrival, out, {d: merged[d] for d in sorted(merged)}


def main():
    cutoff_s = os.environ["WEATHER_CUTOFF"]
    cutoff = dt.datetime(*map(int, cutoff_s.split("-")), tzinfo=dt.timezone.utc).timestamp()
    observed = float(os.environ["WEATHER_OBSERVED_AT"]) if os.environ.get("WEATHER_OBSERVED_AT") else None
    pre_last = sys.argv[1] if len(sys.argv) > 1 else "08-20"

    con = CS.build_index()
    rows = CS.author_stream(con, cutoff=cutoff, observed_at=observed)
    arrival, cohorts, pre = panel(rows, pre_last)

    days = sorted({DAY(t) for t, _ in rows})
    newest = days[-1]
    pre_n = sum(1 for c in arrival.values() if c <= pre_last)

    emit = {"cutoff": cutoff_s, "newest_day": newest, "pre_event_last_day": pre_last,
            "pre_event_authors": pre_n, "pre_event_by_day": pre, "cohorts": cohorts}

    print(f"pre-event population (arrival <= {pre_last}): {pre_n} authors")
    print(f"{'day':6s} {'active':>7s} {'items':>7s} {'items/author':>13s}")
    for d in days:
        v = pre.get(d, {"authors": 0, "items": 0})
        ipa = v["items"] / v["authors"] if v["authors"] else 0.0
        print(f"{d:6s} {v['authors']:7d} {v['items']:7d} {ipa:13.2f}")

    print(f"\nevent cohorts on {newest} (fixed membership):")
    print(f"{'cohort':7s} {'n':>5s} {'active':>7s} {'retained%':>10s} {'items':>7s} {'items/active':>13s}")
    retained = {}
    for c in sorted(cohorts):
        if c <= pre_last: continue
        n = sum(1 for a, ac in arrival.items() if ac == c)
        v = cohorts[c].get(newest, {"authors": 0, "items": 0})
        pct = round(100 * v["authors"] / n, 1) if n else None
        ipa = round(v["items"] / v["authors"], 2) if v["authors"] else 0.0
        retained[c] = {"n": n, "active": v["authors"], "retained_pct": pct,
                       "items": v["items"], "items_per_active": ipa}
        print(f"{c:7s} {n:5d} {v['authors']:7d} {pct:10.1f} {v['items']:7d} {ipa:13.2f}")
    emit["retained_on_newest_day"] = retained

    # Is the pre-event partition's trajectory a CHANGE? "Flat" is an affirmative claim in this
    # series, so it gets a number rather than an adjective. Poisson counting noise on the two
    # period means is a FLOOR: consecutive days are autocorrelated and the panel is a fixed finite
    # population, both of which make the real interval wider than this.
    def _mean_se(days, field):
        xs = [pre[d][field] for d in days if d in pre]
        m = sum(xs) / len(xs)
        return round(m, 1), round((m / len(xs)) ** 0.5, 2), xs

    base_days = [d for d in days if d <= pre_last][-7:]
    ev_days = [d for d in days if d > pre_last]
    cmp = {}
    for field in ("authors", "items"):
        bm, bse, bxs = _mean_se(base_days, field)
        em, ese, exs = _mean_se(ev_days, field)
        se = round((bse ** 2 + ese ** 2) ** 0.5, 2)
        cmp[field] = {"baseline_days": base_days, "baseline_series": bxs, "baseline_mean": bm,
                      "event_days": ev_days, "event_series": exs, "event_mean": em,
                      "difference": round(em - bm, 1), "poisson_se_floor": se,
                      "difference_in_se": round((em - bm) / se, 2) if se else None,
                      "ranges_overlap": not (max(exs) < min(bxs) or min(exs) > max(bxs))}
    cmp["note"] = ("Poisson counting only, and a FLOOR on the noise: day-to-day counts within one"
                   " fixed panel are autocorrelated. The baseline window is itself trending, so"
                   " read the difference against that trend, not as a level shift.")
    emit["pre_event_baseline_vs_event"] = cmp
    print(f"\npre-event panel, last {len(base_days)} baseline days vs the {len(ev_days)} event days:")
    for field in ("authors", "items"):
        c = cmp[field]
        print(f"  {field:8s} {c['baseline_mean']:7.1f} -> {c['event_mean']:7.1f}  "
              f"diff {c['difference']:+7.1f}  = {c['difference_in_se']:+5.2f} Poisson SE "
              f"(floor)   ranges overlap: {c['ranges_overlap']}")

    S = Path(os.environ.get("MEMETIC_WORKDIR", Path.home() / "personal/memetic-workdir"))
    json.dump(emit, open(S / "weather_retention_panel.json", "w"), indent=1)
    print(f"\nsaved {S / 'weather_retention_panel.json'}")


if __name__ == "__main__":
    main()
