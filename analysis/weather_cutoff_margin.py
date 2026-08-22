#!/usr/bin/env python3
"""How much margin the pull had over the cutoff, and what the cutoff excluded.

Every issue states its cutoff, but the MARGIN -- how long after the cutoff the pull actually ran --
has been prose rather than a measurement, and it matters for one instrument in particular. Backfill
is detected by comparing the previous pull's corpus with this one, so a longer gap gives a
late-arriving item more time to appear before the comparison is taken. Issues #3-#7 all pulled ~3 h
after their cutoff; issue #8 ran a day late and pulled 23.7 h after it, which makes its feed-lag
zero a STRONGER negative than theirs rather than a comparable one. A report that does not publish
the margin cannot say that.

Also reports what the cutoff threw away. A late pull holds a large block of post-cutoff items
(issue #8: 807 items covering nearly all of 08-21) that are correctly excluded from every cell but
should be visible, so a reader can see the analysis choice rather than infer it.

Usage: WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_cutoff_margin.py [pull_at_iso]
       pull_at_iso defaults to data/manifest.json's pulled_at_utc.
"""
import json, os, sys, datetime as dt
from pathlib import Path

D = Path("/home/dan/personal/memetic/data/posts")
MANIFEST = Path("/home/dan/personal/memetic/data/manifest.json")
_iso = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_times(d=D, min_chars=20):
    """-> sorted epoch seconds of every item of at least `min_chars`, no cutoff applied."""
    ts = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t / 1000 if t > 1e12 else t
        if len(((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()) >= min_chars:
            ts.append(t)
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc / 1000 if tc > 1e12 else tc
            if len((c.get("body") or "").strip()) >= min_chars:
                ts.append(tc)
    return sorted(ts)


def margins(cutoff_str, pull_at=None, d=D):
    """-> the cutoff/pull margin block for a weather results.json."""
    cut = dt.datetime(*map(int, cutoff_str.split("-")), tzinfo=dt.timezone.utc).timestamp()
    if pull_at is None:
        pull_at = json.load(open(MANIFEST))["pulled_at_utc"]
    pt = dt.datetime.strptime(pull_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
    ts = load_times(d)
    ins = [t for t in ts if t < cut]
    out = [t for t in ts if t >= cut]
    return {
        "cutoff_utc": _iso(cut), "pull_at_utc": pull_at,
        "pull_margin_hours": round((pt - cut) / 3600, 1),
        "in_scope_items": len(ins), "last_in_scope_item_utc": _iso(ins[-1]) if ins else None,
        "last_in_scope_gap_to_cutoff_hours": round((cut - ins[-1]) / 3600, 2) if ins else None,
        "post_cutoff_items_excluded": len(out),
        "post_cutoff_span_utc": [_iso(out[0]), _iso(out[-1])] if out else None,
        "note": "the pull margin is what makes the feed-lag instrument's sensitivity comparable (or "
                "not) across issues: backfill is found by diffing the previous pull against this "
                "one, so a longer margin gives late items more time to show up. Post-cutoff items "
                "are pulled and correctly excluded from every cell.",
    }


if __name__ == "__main__":
    print(json.dumps(margins(os.environ["WEATHER_CUTOFF"],
                             sys.argv[1] if len(sys.argv) > 1 else None), indent=1))
