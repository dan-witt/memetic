#!/usr/bin/env python3
"""Reproduce a published weather issue from the observation store alone.

The store is only worth having if it can stand in for the directory-of-JSON it replaces. This
rebuilds a published issue's corpus block, inflow table, churn signature and feed-lag cells from
SQLite queries against data/observations.jsonl -- no corpus tree, no git checkout, no prev_corpus
snapshot -- and diffs every cell against the results.json that shipped.

Two cells are worth watching because they are where the store is not merely a faster path but a
different (and more honest) construction:

  backfill   the directory version compares against `prev_last`, the last item that happened to be
             in the previous corpus. That was never a chosen boundary, just an artifact of what the
             previous pull caught. The store makes it a named basis: prev_last_item reproduces the
             series, prev_run is the stricter reading. At issue #10 they differ by one item, in an
             82-second gap between the previous corpus's last item and the previous pull's clock.
  edits      the directory version can only see an edit by diffing two whole corpora, which is why
             the weather pipeline re-reads ~1,800 threads per issue. Here it is a row with
             version='edit'.

Usage: python3 analysis/corpus_verify.py [ISSUE_DATE]     (default 2026-08-22, issue #10)
"""
import collections, datetime as dt, json, sqlite3, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS
from weather_churn import signature_windows
from weather_cutoff_margin import _parse_stamp

REPO = Path(__file__).resolve().parent.parent
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def check(results, label, got, want):
    ok = got == want
    results.append(ok)
    flag = "ok  " if ok else "FAIL"
    print(f"  [{flag}] {label:34s} store={got!s:<22s} published={want!s}")
    return ok


def verify(issue_date):
    pub = json.load(open(REPO / "results" / "weather" / issue_date / "results.json"))
    cutoff = _parse_stamp(pub["cutoff"])
    observed = _parse_stamp(pub["pull_at"])
    con = sqlite3.connect(CS.DB)
    rows = CS.items_at(con, cutoff=cutoff, observed_at=observed)
    R = []

    print(f"\n=== {pub['issue']} — rebuilt from the observation store ===")
    print(f"    cutoff {pub['cutoff']}   observed_at {pub['pull_at']}   {len(rows)} items\n")

    print("corpus")
    want = pub["corpus"]
    check(R, "items", len(rows), want["items"])
    check(R, "posts", sum(1 for r in rows if r["kind"] == "post"), want["posts"])
    check(R, "authors", len({r["author"] for r in rows}), want["authors"])
    check(R, "days", sorted({DAY(r["created_at"]) for r in rows}), want["days"])

    print("\ninflows (per day)")
    first, new, items_, active, newc = {}, collections.Counter(), collections.Counter(), \
        collections.defaultdict(set), collections.Counter()
    for r in rows:
        d, a = DAY(r["created_at"]), r["author"]
        items_[d] += 1; active[d].add(a)
        if a not in first:
            first[a] = d; new[d] += 1
        if first[a] == d:
            newc[d] += 1
    bad = []
    for d in sorted(items_):
        w = pub["structure"]["inflows"][d]
        got = (new[d], len(active[d]), items_[d], round(newc[d] / items_[d], 3))
        exp = (w["new_authors"], w["active_authors"], w["items"], w["newcomer_item_share"])
        if got != exp:
            bad.append((d, got, exp))
    check(R, f"all {len(items_)} days match", bad, [])

    print("\nday-window churn signature")
    sig = signature_windows([(DAY(r["created_at"]), r["author"]) for r in rows])
    for k in ("core_n", "core_dominance_pct", "stability_ratio", "permeability_pct"):
        check(R, k, sig[k], pub["structure"]["churn_signature_day_K3"][k])

    print("\nfeed lag (a query here, a corpus diff in the directory version)")
    fl = pub["feed_lag"]
    bf = [b for b in CS.backfill(con, basis="prev_last_item")
          if abs(b["observed_at"] - observed) < 1]
    check(R, "backfilled_items", len(bf), fl["backfilled_items"])
    check(R, "by_day", dict(collections.Counter(DAY(b["created_at"]) for b in bf)), fl["by_day"])
    check(R, "new_authors_revealed", sum(1 for b in bf if b["reveals_author"]),
          fl["new_authors_revealed"])
    if bf:
        ages = sorted(b["age_at_missed_pull_h"] for b in bf)
        check(R, "item age at missed pull (median)", round(ages[len(ages) // 2], 2),
              fl["item_age_at_missed_pull_hours"]["median"])
    ed = [e for e in CS.edits(con) if abs(e["first_seen_at"] - observed) < 1]
    check(R, "edited_items", len(ed), fl["content_mutations"]["edited_items"])

    strict = [b for b in CS.backfill(con, basis="prev_run") if abs(b["observed_at"] - observed) < 1]
    print(f"\n    (basis note: prev_last_item -> {len(bf)} backfilled, matching the series; "
          f"prev_run -> {len(strict)}. The directory version could express only the first, "
          f"implicitly.)")

    print(f"\n{sum(R)}/{len(R)} cells reproduced" + ("" if all(R) else "  *** FAILURES ***"))
    return all(R)


if __name__ == "__main__":
    sys.exit(0 if verify(sys.argv[1] if len(sys.argv) > 1 else "2026-08-22") else 1)
