#!/usr/bin/env python3
"""How much margin the pull had over the cutoff, and what the cutoff excluded.

Every issue states its cutoff, but the MARGIN -- how long after the cutoff the pull actually ran --
has been prose rather than a measurement, and it matters for one instrument in particular. Backfill
is detected by comparing the previous pull's corpus with this one, so a longer gap gives a
late-arriving item more time to appear before the comparison is taken. Issue #8 ran a day late and
pulled 23.7 h after its cutoff, which makes its feed-lag zero a STRONGER negative than a
short-margin issue's rather than a comparable one. A report that does not publish the margin cannot
say that.

Also reports what the cutoff threw away. A late pull holds a large block of post-cutoff items
(issue #8: 807 items covering nearly all of 08-21) that are correctly excluded from every cell but
should be visible, so a reader can see the analysis choice rather than infer it.

history() DERIVES the margin record from the published issues rather than asserting it. This
docstring used to claim "issues #3-#7 all pulled ~3 h after their cutoff"; the derived record is
0.2, 5.2, 4.5, 2.9, 3.0 -- a 0.2-to-5.2 h spread, and issue #3's 11 minutes is SHORTER than any
issue since. Quote history(), not a remembered average.

Usage: WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_cutoff_margin.py [pull_at_iso]
       pull_at_iso defaults to data/manifest.json's pulled_at_utc.
       python3 analysis/weather_cutoff_margin.py --history   (the derived per-issue record)
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
    """LEGACY (issues #3-#10): the margin computed by globbing the corpus directory and trusting
    data/manifest.json for the pull time. Kept so those issues stay reproducible. New issues should
    use margin_from_store(), which reads the run log and returns coverage alongside the margin --
    manifest.json describes only the last run, and describes it as though it were the corpus."""
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


RESULTS = Path("/home/dan/personal/memetic/results/weather")
# published pull_at fields are not all strict ISO: issues #3 and #4 wrote prose after the stamp,
# and #3 wrote minute precision. Try the fixed prefixes longest-first -- deterministic, no regex.
_PULL_FORMATS = [(20, "%Y-%m-%dT%H:%M:%SZ"), (19, "%Y-%m-%dT%H:%M:%S"), (16, "%Y-%m-%dT%H:%M")]


def _parse_stamp(s):
    """-> epoch seconds for a published pull_at string, or None if it carries no stamp."""
    if not s:
        return None
    for n, fmt in _PULL_FORMATS:
        try:
            return dt.datetime.strptime(s[:n], fmt).replace(tzinfo=dt.timezone.utc).timestamp()
        except ValueError:
            continue
    return None


def history(results=RESULTS):
    """-> [{issue, cutoff, pull_at, margin_hours, backfilled_items, edited_items}] per published
    issue, oldest first. Derived from each issue's own results.json, so it cannot go stale the way
    a prose summary does. margin_hours is None for issues that published no pull timestamp."""
    rows = []
    for q in sorted(Path(results).glob("*/results.json")):
        d = json.load(q.open())
        cut, pull = d.get("cutoff"), d.get("pull_at")
        ct, pt = _parse_stamp(cut), _parse_stamp(pull)
        fl = d.get("feed_lag") or {}
        bf = fl.get("backfilled_items")
        # Adopted at issue #11 (issue #10's watch item #8): counts are not comparable across days
        # of different size. 08-22 carried ~3x the traffic of the days before it, so a raw count of
        # 7 and a raw count of 2 sat on very different denominators.
        win = (d.get("corpus") or {}).get("issue_window_items")
        rows.append({
            "issue": q.parent.name,
            "cutoff_utc": cut,
            "pull_at_utc": pull,
            "pull_margin_hours": round((pt - ct) / 3600, 2) if (ct and pt) else None,
            "backfilled_items": bf,
            "issue_window_items": win,
            "backfill_per_1000_window_items": round(1000 * bf / win, 2)
            if (bf is not None and win) else None,
            "edited_items": (fl.get("content_mutations") or {}).get("edited_items"),
        })
    return rows


def margin_from_store(cutoff_str, con=None):
    """The cutoff/pull margin taken from the FETCH RUN LOG rather than data/manifest.json.

    manifest.json describes the last run only, and describes it as though it were the corpus: a
    2026-08-23 run that saved 674 of 1,801 threads wrote a manifest that read like a complete pull,
    and nothing in the data contradicted it. The run log records every run including partial ones,
    so the margin can be reported alongside the coverage it was measured at -- which is the pair a
    reader actually needs.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    import corpus_store as CS
    con = con or CS.build_index()
    cut = dt.datetime(*map(int, cutoff_str.split("-")), tzinfo=dt.timezone.utc).timestamp()
    row = con.execute("SELECT run_id, ended_at, mode, threads_ok, threads_429, complete "
                      "FROM fetch_runs WHERE ended_at >= ? ORDER BY ended_at LIMIT 1",
                      (cut,)).fetchone()
    if not row:
        return None
    run_id, ended, mode, ok, e429, complete = row
    # only what this run had OBSERVED -- counting everything we know now would describe a corpus
    # the issue never saw, which is precisely the confusion the store exists to remove
    ins_rows = CS.items_at(con, cutoff=cut, observed_at=ended)
    ins = (max((r["created_at"] for r in ins_rows), default=None), len(ins_rows))
    out = len(CS.items_at(con, cutoff=None, observed_at=ended)) - ins[1]
    return {
        "cutoff_utc": _iso(cut), "pull_at_utc": _iso(ended), "run_id": run_id, "mode": mode,
        "pull_margin_hours": round((ended - cut) / 3600, 2),
        "in_scope_items": ins[1], "last_in_scope_item_utc": _iso(ins[0]) if ins[0] else None,
        "last_in_scope_gap_to_cutoff_hours": round((cut - ins[0]) / 3600, 2) if ins[0] else None,
        "post_cutoff_items_excluded": out,
        "run_complete": bool(complete), "threads_ok": ok, "threads_429": e429,
        "coverage": CS.coverage(con),
        "note": "margin AND coverage together: a margin means little if the run behind it verified "
                "only part of the corpus, which the manifest alone could not express.",
    }


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--history" in argv:
        print(json.dumps(history(), indent=1))
    elif "--legacy" in argv:
        rest = [a for a in argv if not a.startswith("-")]
        print(json.dumps(margins(os.environ["WEATHER_CUTOFF"],
                                 rest[0] if rest else None), indent=1))
    else:
        print(json.dumps(margin_from_store(os.environ["WEATHER_CUTOFF"]), indent=1))
