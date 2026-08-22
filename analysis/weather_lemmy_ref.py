#!/usr/bin/env python3
"""Lemmy.world reference levels for the weather report's allocation section.

The weather report's allocation trend has always been read against the Usenet anchors' Qwen band
(0.085-0.221) and the human-calibrated ~0.06 floor. Both are single-topic groups. Since
results/lemmy_baseline, there is also a matched human *platform* founding to read against, and it
sits an order of magnitude higher than the anchors — a venue share the square's oscillation band
does not clear. Carrying it here means every issue picks the levels up automatically instead of
someone remembering to retype them.

These are FROZEN: lemmy.world's founding month is a fixed 2023 corpus and is never re-measured.
The values are read from the baseline's own emitted artifact so the two cannot drift apart.
"""
import json
from pathlib import Path

BASELINE = Path("/home/dan/personal/memetic/results/lemmy_baseline/results.json")


def levels(path=BASELINE):
    """-> the lemmy reference block for a weather results.json, or None if the baseline is absent."""
    if not Path(path).exists():
        return None
    d = json.load(open(path))
    a = d["allocation"]["all_items"]
    g = lambda norm, key: a[norm][key]["point"]
    return {
        "source": "results/lemmy_baseline/results.json (frozen; 2023-06 founding month, 55,223 items)",
        "currency": "Qwen binary, same classifier and prompt as the weather allocation cell",
        "platform_qwen": g("qwen", "share_lemmy_all"),
        "platform_gemma": g("gemma", "share_lemmy_all"),
        "topic_tier_qwen": g("qwen", "share_lemmy_topic"),
        "meta_tier_qwen": g("qwen", "share_lemmy_meta"),
        "note": "the platform figure is the like-for-like comparator (both venues carry their own "
                "governance in one undifferentiated stream); the topic tier is what the square is "
                "robustly above and the meta tier is what a venue whose remit IS the venue reads. "
                "A weather point BELOW platform_qwen means the square allocated less attention to "
                "itself that day than a human platform founding did.",
    }


def position(share_qwen, ref=None):
    """Where a day's venue share sits against the lemmy levels. Ratios, not verdicts."""
    ref = ref or levels()
    if ref is None or share_qwen is None:
        return None
    return {"vs_platform": round(share_qwen / ref["platform_qwen"], 3),
            "vs_topic_tier": round(share_qwen / ref["topic_tier_qwen"], 3),
            "above_platform": bool(share_qwen > ref["platform_qwen"])}


def coverage_bound(path=BASELINE, corpus_items=55223):
    """Worst-case effect of the comparator's own unparsed-answer bias on platform_qwen.

    Issue #7 found the square's allocation classifier fails ONE-SIDEDLY: every unparseable answer
    is the verbatim string "SUBJECT MATTER", i.e. a WORLD answer the strict parse throws away, so
    dropping those items biases the square's venue share UPWARD (analysis/weather_label_failures.py).
    The comparator was classified with the identical prompt and model, so it carries the same bias
    and a correction applied to one side only would be a rigged comparison.

    This bounds the comparator's side WITHOUT re-measuring the frozen corpus: n_classified is
    published, the founding-month item count is published, and the difference is an upper bound on
    how many items the parse dropped. Counting every one of them WORLD gives the lowest platform
    figure the correction could produce. It is a BOUND, not the correction: some of that difference
    is invalid claims rather than unparsed answers, so the true move is smaller.
    """
    if not Path(path).exists():
        return None
    d = json.load(open(path))
    a = d["allocation"]["all_items"]["qwen"]
    n = a["n"]["lemmy_all"]
    share = a["share_lemmy_all"]["point"]
    v = round(share * n)
    uncovered_max = max(0, corpus_items - n)
    return {"platform_qwen_published": share, "n_classified": n, "venue_items": v,
            "uncovered_upper_bound": uncovered_max,
            "uncovered_pct_upper_bound": round(100 * uncovered_max / corpus_items, 3),
            "platform_qwen_worst_case": round(v / (n + uncovered_max), 4),
            "max_downward_move": round(v / (n + uncovered_max) - share, 4),
            "note": "upper bound on the comparator's own coverage bias; the square's same-parse "
                    "correction is an order of magnitude larger, so correcting BOTH sides widens "
                    "the square's shortfall against the platform rather than closing it."}


def corrected_platform(path=BASELINE, workdir=None):
    """The comparator's platform figure under issue #8's CORRECTED parse — exact, not a bound.

    `coverage_bound` above is the worst case issue #7 could compute without the comparator's raw
    answers: every dropped item counted WORLD. Issue #8 recovered those answers
    (`analysis/weather_lemmy_recover.py`) and can therefore apply the identical corrected parse
    to both sides of the comparison, which is the only way the square's own correction is honest.

    The frozen corpus is not re-measured: the published V/W labels are read as-is, and only the
    items the published run left UNLABELLED were put back through the frozen prompt. Items whose
    claim is invalid are excluded from the denominator on both sides and are not recovered.

    -> dict, or None if the recovery artifact is absent (then use coverage_bound instead).
    """
    import os
    S = Path(workdir or os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
    art, lab_f = S / "allocation_unparsed_raw_lemmy.json", S / "allocation_labels_lemmy.json"
    if not (art.exists() and lab_f.exists()):
        return None
    import weather_alloc_parse as AP
    lab = json.load(open(lab_f))["lemmy"]
    rec = json.load(open(art))
    n_pub = sum(1 for x in lab if x in ("V", "W"))
    v_pub = sum(1 for x in lab if x == "V")
    add = [AP.corrected(w) for w in rec["raw"]]
    v_add, n_add = sum(1 for l in add if l == "V"), sum(1 for l in add if l in ("V", "W"))
    published = json.load(open(path))["allocation"]["all_items"]["qwen"]["share_lemmy_all"]["point"]
    return {
        "platform_qwen_published_strict": published,
        "platform_qwen_strict_recomputed": round(v_pub / n_pub, 4),
        "n_strict": n_pub, "venue_strict": v_pub,
        "recovered_answers": len(rec["raw"]),
        "recovered_labelled": n_add, "recovered_venue": v_add,
        "recovered_still_unparseable": len(rec["raw"]) - n_add,
        "one_sided": bool(n_add and v_add == 0),
        "platform_qwen_corrected": round((v_pub + v_add) / (n_pub + n_add), 4),
        "move": round((v_pub + v_add) / (n_pub + n_add) - v_pub / n_pub, 4),
        # The one recovered answer that is not a WORLD phrasing ("COMMUNITY") is semantically a
        # VENUE answer but is left unparsed on purpose -- reading it that way is a judgement about
        # meaning, not a parse. Size the choice rather than asserting it is negligible.
        "unparsed_as_venue_move": round(
            (v_pub + v_add + (len(rec["raw"]) - n_add)) / (n_pub + len(rec["raw"]))
            - (v_pub + v_add) / (n_pub + n_add), 7),
        # The frozen baseline publishes n = 55,152 classified; the label cache it was computed from
        # carries one more V/W label than that. The difference is one item and is not explained by
        # invalid claims (every labelled item has a valid claim). Both denominators give 0.4665 to
        # four decimals and both corrections give 0.4660, so no published digit turns on it -- but
        # a figure sold as EXACT has to show the discrepancy rather than absorb it.
        "n_published_by_baseline": json.load(open(path))["allocation"]["all_items"]["qwen"]["n"]["lemmy_all"],
        "n_minus_baseline_n": n_pub - json.load(open(path))["allocation"]["all_items"]["qwen"]["n"]["lemmy_all"],
        "invalid_claim_items_excluded": rec["n_invalid_claim"],
        "note": "exact corrected-parse figure for the comparator, replacing issue #7's worst-case "
                "bound. The published labels are untouched; only the dropped items were re-parsed.",
    }


if __name__ == "__main__":
    print(json.dumps({"levels": levels(), "coverage_bound": coverage_bound(),
                      "corrected_platform": corrected_platform()}, indent=1))
