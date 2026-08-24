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
import weather_issue_boundary as IB

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
    # Rebuild rather than open: the index is DERIVED, so verifying against whatever happens to be
    # on disk can pass or fail on a stale index instead of on the log the store actually holds.
    con = CS.build_index()
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
    # ISSUE TO ISSUE, explicitly. Letting backfill() fall back to consecutive observation times
    # measures the gap between the last two RUNS, which stopped being the same thing the moment
    # catch-up runs landed between two issues: at issue #11 that fallback gives 5 where the
    # published window (previous issue's pull -> this issue's pull) gives 3. weather_cpu.py passes
    # these boundaries; so must the verifier, or it can never confirm an issue as published.
    prev_at = IB.previous_issue_observed_at(pub["cutoff"][:10])
    bf = CS.backfill(con, prev_at=prev_at, this_at=observed, basis="prev_last_item")
    check(R, "backfilled_items", len(bf), fl["backfilled_items"])
    check(R, "by_day", dict(collections.Counter(DAY(b["created_at"]) for b in bf)), fl["by_day"])
    check(R, "new_authors_revealed", sum(1 for b in bf if b["reveals_author"]),
          fl["new_authors_revealed"])
    if bf:
        ages = sorted(b["age_at_missed_pull_h"] for b in bf)
        check(R, "item age at missed pull (median)", round(ages[len(ages) // 2], 2),
              fl["item_age_at_missed_pull_hours"]["median"])
    ed = CS.edits(con, since=prev_at, until=observed)
    check(R, "edited_items", len(ed), fl["content_mutations"]["edited_items"])

    strict = CS.backfill(con, prev_at=prev_at, this_at=observed, basis="prev_run")
    print(f"\n    (basis note: prev_last_item -> {len(bf)} backfilled, matching the series; "
          f"prev_run -> {len(strict)}. The directory version could express only the first, "
          f"implicitly.)")

    print(f"\n{sum(R)}/{len(R)} cells reproduced" + ("" if all(R) else "  *** FAILURES ***"))
    return all(R)


def verify_gpu_output(issue_date, out_path=None):
    """Diff a store-backed weather_gpu.py run against the published issue.

    RESULT cells only. The audit counters (delta_classified, retries_in_previous_pull) describe
    WORK DONE by a particular run, so a re-run with warm caches legitimately reports different
    numbers -- comparing those would fail for the right reason and tell us nothing.
    """
    import os
    out_path = out_path or Path(os.environ.get("MEMETIC_WORKDIR",
                                Path.home() / "personal/memetic-workdir")) / "weather_gpu_out.json"
    got = json.load(open(out_path))
    pub = json.load(open(REPO / "results" / "weather" / issue_date / "results.json"))
    at = pub["allocation_trend"]
    R = []
    print(f"\n=== weather_gpu.py output vs published {pub['issue']} ===\n")

    print("allocation")
    check(R, "venue share/day (strict)", got["allocation_daily_venue_share"],
          at["venue_share_per_day_qwen_binary"])
    check(R, "venue share/day (corrected)", got["allocation_daily_venue_share_corrected"],
          at["venue_share_per_day_corrected_parse"])
    check(R, "unlabelled after run", got["allocation_label_audit"]["unlabelled_after_run"],
          at["label_audit"]["unlabelled_after_run"])
    check(R, "published days moved", got["allocation_label_audit"]["published_days_moved"],
          at["label_audit"]["published_days_moved"])
    check(R, "vs lemmy per day", got["allocation_daily_vs_lemmy"], at["vs_lemmy_per_day"])

    print("\nplacement (three embedders, full + window)")
    for emb, fams in pub["placement_vs_frozen_anchors"].items():
        for fam, cells in fams.items():
            for scope in ("full", "window_only"):
                check(R, f"{emb} {fam} {scope}", got["placement"][emb][fam][scope],
                      cells[scope])

    print("\nidea series + newcomer")
    check(R, "rolling halves", got["rolling_halves_bge"], pub["idea_time_series"]["halves"])
    check(R, "newcomer counts", got["newcomer_counts"],
          pub["newcomer_cells_issue_window"]["counts"])
    check(R, "within-pool parity", got["newcomer_within_pool_parity"],
          pub["newcomer_cells_issue_window"]["within_pool_parity"])
    check(R, "union over incumbent", got["refresh_union_over_incumbent"],
          pub["newcomer_cells_issue_window"]["union_over_incumbent"])
    check(R, "NN matched", got["refresh_nn_distance_matched"],
          pub["newcomer_cells_issue_window"]["nn_distance_matched"])

    print("\nwindow basis")
    check(R, "issue_window_items", got["issue_window_items"], pub["corpus"]["issue_window_items"])

    print(f"\n{sum(R)}/{len(R)} cells reproduced" + ("" if all(R) else "  *** FAILURES ***"))
    return all(R)


def verify_cpu_output(issue_date, out_path=None):
    """Diff a store-backed weather_cpu.py run against the published issue, cell for cell.

    corpus_verify's other half rebuilds cells with its own queries; this one checks the ACTUAL
    pipeline output, so a port that quietly changed a definition cannot pass by agreeing with a
    re-implementation of itself.
    """
    import os
    out_path = out_path or Path(os.environ.get("MEMETIC_WORKDIR",
                                Path.home() / "personal/memetic-workdir")) / "weather_cpu_out.json"
    got = json.load(open(out_path))
    pub = json.load(open(REPO / "results" / "weather" / issue_date / "results.json"))
    R = []
    print(f"\n=== weather_cpu.py output vs published {pub['issue']} ===\n")

    print("corpus")
    for k in ("items", "posts", "authors", "issue_window_items"):
        check(R, k, got["corpus"][k], pub["corpus"][k])

    print("\ninflows")
    bad = [d for d in pub["structure"]["inflows"]
           if got["inflows"].get(d) != pub["structure"]["inflows"][d]]
    check(R, f"all {len(pub['structure']['inflows'])} days", bad, [])

    print("\nchurn + activity clock")
    for k in ("core_n", "core_dominance_pct", "stability_ratio", "permeability_pct"):
        check(R, f"day-window {k}", got["churn_signature_day_K3"][k],
              pub["structure"]["churn_signature_day_K3"][k])
    for fam, sig in pub["structure"]["activity_clock_signatures"]["signatures"].items():
        g = got["activity_clock_signatures"]["signatures"][fam]
        check(R, f"clock {fam}", [g[k] for k in ("core_dominance_pct", "stability_ratio",
                                                 "permeability_pct")],
              [sig[k] for k in ("core_dominance_pct", "stability_ratio", "permeability_pct")])

    print("\nregister (zstd)")
    check(R, "whole", got["zstd_raw"]["whole"], pub["register_trend_zstd_raw"]["whole"])
    bad = [d for d in pub["register_trend_zstd_raw"]["per_day"]
           if got["zstd_raw"]["per_day"].get(d) != pub["register_trend_zstd_raw"]["per_day"][d]]
    check(R, "per-day series", bad, [])

    print("\nfeed lag")
    g, w = got["feed_lag"], pub["feed_lag"]
    for k in ("backfilled_items", "by_day", "new_authors_revealed"):
        check(R, k, g[k], w[k])
    check(R, "item age median", g["item_age_at_missed_pull_hours"]["median"],
          w["item_age_at_missed_pull_hours"]["median"])
    for k in ("edited_items", "items_compared", "authors_affected"):
        check(R, f"mutations {k}", g["content_mutations"][k], w["content_mutations"][k])

    print("\ncohort survival")
    bad = [d for d in pub["structure"]["cohort_survival"]
           if got["cohort_survival"].get(d) != pub["structure"]["cohort_survival"][d]]
    check(R, f"all {len(pub['structure']['cohort_survival'])} cohorts", bad, [])

    print(f"\n{sum(R)}/{len(R)} cells reproduced" + ("" if all(R) else "  *** FAILURES ***"))
    return all(R)


if __name__ == "__main__":
    date = [a for a in sys.argv[1:] if not a.startswith("-")]
    date = date[0] if date else "2026-08-22"
    if "--cpu" in sys.argv:
        sys.exit(0 if verify_cpu_output(date) else 1)
    if "--gpu" in sys.argv:
        sys.exit(0 if verify_gpu_output(date) else 1)
    sys.exit(0 if verify(date) else 1)
