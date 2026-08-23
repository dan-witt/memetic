#!/usr/bin/env python3
"""What an arrival day actually looks like, so a report can describe an influx instead of guessing.

Issue #10 landed 258 new authors in one calendar day -- more than the founding day's 224 -- and the
first question a reader asks is whether that is a community event or an instrument artefact (a
scripted onboarding, one operator behind many identities, a pull that finally caught up on old
threads). None of those are answerable from a headcount, and every one of them is cheap to probe:

  arrivals_by_hour      a scripted onboarding clusters; a community event spreads
  items_per_author      one flood account looks nothing like 258 people posting a handful each
  chars_per_item        a bot run is usually short and uniform against the day's incumbents
  threads_touched       arrivals confined to one thread are a thread, not an influx
  model_label_mix       the PLATFORM-PROVIDED author_model label, newcomers vs incumbents; a single
                        model family dominating the arrivals would be a mechanism worth naming

The model mix uses the platform's own label and nothing else. It is not an author clustering, and
identity remains forum identity, never operator (see any issue's caveats).

Every cell here is DESCRIPTIVE. None of it is a test, and a negative on all five is not proof that
an influx is organic -- it only says the cheap artefact explanations do not fit.

Usage: WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_influx_profile.py [MM-DD ...]
       days default to the last calendar day below the cutoff.
"""
import json, os, statistics as st, sys, datetime as dt
from collections import Counter, defaultdict
from pathlib import Path

D = Path("/home/dan/personal/memetic/data/posts")
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
HOUR = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).hour


def load(cutoff, d=D, min_chars=20):
    """-> [(epoch, author, model, chars, thread_id)] for every in-scope item below the cutoff.

    Same inclusion rule as the rest of the pipeline: post = title+body, comment = body, >= 20 chars.
    """
    out = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t / 1000 if t > 1e12 else t
        body = ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()
        rows = [(t, p.get("author") or "?", p.get("author_model"), len(body))]
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc / 1000 if tc > 1e12 else tc
            cb = (c.get("body") or "").strip()
            rows.append((tc, c.get("author") or "?", c.get("author_model"), len(cb)))
        out += [(ts, a, m, n, f.stem) for ts, a, m, n in rows if ts < cutoff and n >= min_chars]
    return sorted(out)


def profile(items, day, top_models=6):
    """-> the descriptive block for one calendar day."""
    first = {}
    for t, a, _, _, _ in items:
        if a not in first or t < first[a]:
            first[a] = t
    today = [r for r in items if DAY(r[0]) == day]
    if not today:
        return None
    arrivals = sorted(a for a, t in first.items() if DAY(t) == day)
    new = [r for r in today if DAY(first[r[1]]) == day]
    inc = [r for r in today if DAY(first[r[1]]) != day]
    per_author = Counter(r[1] for r in today)

    def mix(auths):
        c = Counter()
        for a in auths:
            c[next((m for t, aa, m, _, _ in items if aa == a and m), None)] += 1
        tot = sum(c.values()) or 1
        return {"n_authors": tot, "distinct_labels": len(c),
                "top": [[k, round(100 * v / tot, 1)] for k, v in c.most_common(top_models)]}

    hours = Counter(HOUR(first[a]) for a in arrivals)
    hist = [hours.get(h, 0) for h in range(24)]
    busiest = max(hist) if hist else 0
    return {
        "day": day,
        "items": len(today),
        "active_authors": len(per_author),
        "new_authors": len(arrivals),
        "newcomer_items": len(new),
        "incumbent_items": len(inc),
        "newcomer_item_share": round(len(new) / len(today), 3),
        "arrivals_by_hour_utc": hist,
        "arrivals_hours_occupied": sum(1 for h in hist if h),
        "arrivals_busiest_hour_share": round(busiest / max(len(arrivals), 1), 3),
        "items_per_author": {"median": st.median(per_author.values()),
                             "p90": sorted(per_author.values())[int(0.9 * (len(per_author) - 1))],
                             "max": max(per_author.values())},
        "chars_per_item": {
            "day_median": round(st.median(r[3] for r in today)),
            "day_mean": round(st.mean(r[3] for r in today)),
            "newcomer_median": round(st.median(r[3] for r in new)) if new else None,
            "incumbent_median": round(st.median(r[3] for r in inc)) if inc else None,
        },
        "threads_touched": len({r[4] for r in today}),
        "threads_touched_by_newcomers": len({r[4] for r in new}),
        "model_label_mix_newcomers": mix(arrivals),
        "model_label_mix_incumbents_active_today": mix(sorted({r[1] for r in inc})),
        "note": "descriptive only; no test. author_model is the platform's own label. Identity is "
                "forum identity, never operator.",
    }


if __name__ == "__main__":
    _c = os.environ["WEATHER_CUTOFF"]
    cut = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()
    items = load(cut)
    days = [a for a in sys.argv[1:]] or [max(DAY(r[0]) for r in items)]
    emit = {}
    for day in days:
        r = profile(items, day)
        if not r:
            print(f"{day}: no in-scope items"); continue
        emit[day] = r
        print(f"{day}: {r['items']} items, {r['new_authors']} new authors over "
              f"{r['arrivals_hours_occupied']}/24 hours (busiest hour holds "
              f"{100 * r['arrivals_busiest_hour_share']:.0f}% of them), "
              f"{r['items_per_author']['median']} items/author median, max "
              f"{r['items_per_author']['max']}, {r['threads_touched']} threads, "
              f"median {r['chars_per_item']['day_median']} chars "
              f"(newcomers {r['chars_per_item']['newcomer_median']}, "
              f"incumbents {r['chars_per_item']['incumbent_median']})")
        print(f"      arrivals by hour: {r['arrivals_by_hour_utc']}")
        print(f"      newcomer model labels: {r['model_label_mix_newcomers']['distinct_labels']} "
              f"distinct, top {r['model_label_mix_newcomers']['top'][:4]}")
        print(f"      incumbent model labels: "
              f"{r['model_label_mix_incumbents_active_today']['distinct_labels']} distinct, top "
              f"{r['model_label_mix_incumbents_active_today']['top'][:4]}")
    out = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "weather_influx_profile_out.json"
    out.write_text(json.dumps(emit, indent=1))
    print(f"saved {out}")
