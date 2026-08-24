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

import sys as _sys
_sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import corpus_store as CS

_CON = CS.build_index()

D = Path("/home/dan/personal/memetic/data/posts")
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
HOUR = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).hour


def load(cutoff, d=D, min_chars=20, observed_at=None):
    """-> [(epoch, author, model, chars, thread_id, kind)] from the observation store.

    None of these cells need item TEXT, so this never opens a thread file: it is one query. `d` is
    kept so existing call sites keep working.
    """
    return [(t, a, m, n, str(pid), k)
            for t, a, m, n, pid, k in CS.profile_rows(_CON, cutoff=cutoff, observed_at=observed_at,
                                                      min_chars=min_chars)]


ADMIN_AUTHOR = "1f916-agent"   # the platform's own account; exempt from the posting cap


def ceiling_history(items):
    """-> the platform's per-author daily posting cap, and each day against it.

    THE CAP IS 20 COMMENTS PER AUTHOR PER DAY, and it is hard: across the whole corpus no
    non-admin author-day carries a 21st comment. Posts are not capped the same way (most authors
    make 0 or 1, a handful make more), so the modal per-author daily maximum is 1 post + 20
    comments = 21 -- which is why the influx profile's "max" column reads 21 on every day of the
    recruitment event and on most days before it.

    This matters for two readings. The "max" column is a PLATFORM CONSTANT, not a behavioural
    signature of an influx. And a day's volume cannot grow by authors posting more without bound:
    past ~21 items per active author a day can only get bigger by recruiting, which is what makes
    items-per-active-author worth reporting beside the raw count.

    Only `1f916-agent` exceeds the cap (up to 47 comments in a day). Its exemption is what produced
    every apparent ceiling breach in the per-day maxima; the one other day above 21 is an author
    who made six POSTS while still stopping at 20 comments.

    Rows carry their kind (corpus_store.profile_rows), because the cap applies to comments and
    not to items; a caller counting items alone cannot see it.
    """
    tot, com, pos = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for r in items:
        t, a = r[0], r[1]
        tot[DAY(t)][a] += 1
        k = r[5] if len(r) > 5 else None
        if k == "comment":
            com[DAY(t)][a] += 1
        elif k == "post":
            pos[DAY(t)][a] += 1
    out = {}
    for day in sorted(tot):
        c = tot[day]
        nonadmin = {a: v for a, v in c.items() if a != ADMIN_AUTHOR}
        mx = max(c.values())
        at_max = sum(1 for v in c.values() if v == mx)
        row = {"authors": len(c), "items": sum(c.values()),
               "items_per_active_author": round(sum(c.values()) / len(c), 2),
               "max_items_per_author": mx, "authors_at_max": at_max,
               "pct_authors_at_max": round(100 * at_max / len(c), 1),
               "max_items_per_author_non_admin": max(nonadmin.values()) if nonadmin else None,
               "author_days_above_21": sorted(a for a, v in c.items() if v > 21)}
        if com[day]:
            cna = {a: v for a, v in com[day].items() if a != ADMIN_AUTHOR}
            row["max_comments_non_admin"] = max(cna.values()) if cna else None
            row["authors_at_comment_cap"] = sum(1 for v in cna.values() if v == 20)
            row["max_posts_non_admin"] = max(
                (v for a, v in pos[day].items() if a != ADMIN_AUTHOR), default=None)
        out[day] = row
    return out


def profile(items, day, top_models=6):
    """-> the descriptive block for one calendar day."""
    first = {}
    for t, a, _, _, _, _ in items:
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
            c[next((m for t, aa, m, _, _, _ in items if aa == a and m), None)] += 1
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
    _obs = float(os.environ["WEATHER_OBSERVED_AT"]) if os.environ.get("WEATHER_OBSERVED_AT") else None
    items = load(cut, observed_at=_obs)
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
    ch = ceiling_history(items)
    emit["_ceiling_history"] = ch
    print("\nper-author daily cap (the 'max' column is a PLATFORM CONSTANT, not a signature):")
    print("  max comments/author/day, non-admin: "
          + "  ".join(f"{d}:{v.get('max_comments_non_admin')}" for d, v in ch.items()))
    print("  items/active author:               "
          + "  ".join(f"{d}:{v['items_per_active_author']}" for d, v in ch.items()))
    breach = {d: v["author_days_above_21"] for d, v in ch.items() if v["author_days_above_21"]}
    print(f"  author-days above 21 items: {sum(len(v) for v in breach.values())} "
          f"-> {breach if breach else 'none'}")
    out = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "weather_influx_profile_out.json"
    out.write_text(json.dumps(emit, indent=1))
    print(f"saved {out}")
