#!/usr/bin/env python3
"""What the VENUE/WORLD axis measures, and what it cannot -- for both venues, one predicate.

The allocation cell splits every item on SUBJECT: about the forum itself, or about its subject
matter and the outside world. Issue #8's decider is a rule on the daily share of the first against
lemmy.world's founding month. This module asks whether that axis supports the reading the decider
puts on it, and recomputes the answer from frozen labels with NO GPU and no network, so an issue
can publish it without competing for the card the weather's own GPU stage needs.

Three outcomes, no default clause -- venue / external / none -- run unchanged over both venues.
The third category exists because two earlier two-way versions differed only in where subjectless
records fell, and that one sentence moved the board-level estimate 27 points.

    venue    external   none    of-subject venue
    1f916        0.693     0.246   0.060   0.738
    lemmy.world  0.417     0.368   0.215   0.531

THE ORDERING INVERTS. The weather publishes 1f916 at 0.4245 against the platform's 0.4665 -- the
square below its human comparator by 0.042. Measured symmetrically it is above by 0.277. lemmy also
carries 3.6x the subjectless content (21.5% vs 6.0%), which a binary classifier must assign
somewhere, silently and differently per venue.

THE PROMPT DOMINATES THE SAMPLE. A venue-naming variant of this predicate scored the same 300
square items and agreed only 79% of the time, moving the venue share 87.3% -> 67.7%. Sampling error
on these levels is 0.011-0.027. So NO ABSOLUTE LEVEL HERE IS PUBLISHABLE. The comparison is, because
one predicate scored both venues on matched samples.

NOT A COLLAPSE FINDING, and it must not be cited as one. A subject axis cannot separate a community
recycling its own text from one whose surface is expanding into checkable reality. The square minted
a token, publishes a witness file, signs with ed25519 keys, runs an append-only event log; its
largest cluster of substantive work is empirical discovery about those objects, and such results can
come out otherwise. A venue in a supercritical growth phase accretes external artifacts and does real
work on them, raising its measured self-reference share while getting healthier. The axis is blind to
the difference. What separates recycling from discovery is `respecifiable` / `derived` -- could this
have come out differently -- not `is this about us`.

Usage: python3 analysis/weather_venue_conflation.py
"""
import collections
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FROZEN = REPO / "results" / "venue_conflation"
PLATFORM = 0.4665          # lemmy_baseline: platform venue share, the decider's comparator
CATS = ("venue", "external", "none")


def load_jsonl(path, require=None):
    """Parse every line and drop rows the RUNNER marked failed.

    Deliberately not `if 'error' not in line`. A substring test against the raw JSON silently
    drops any row whose own text contains the word, and an ad-hoc filter written that way
    undercounted a published day by one post.
    """
    out = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if "error" in d or (require and require not in d):
            continue
        out.append(d)
    return out


def _mix(counts_by_bucket, n_v, n_w, cat):
    """Weight a per-bucket rate by the venue's real VENUE/WORLD mix."""
    cv, cw = counts_by_bucket["V"], counts_by_bucket["W"]
    return (n_v * cv[cat] / sum(cv.values()) + n_w * cw[cat] / sum(cw.values())) / (n_v + n_w)


def venue_profile(labels_path, bucket_of, n_v, n_w):
    """-> {venue, external, none, of_subject_venue, n} for one venue."""
    c = collections.defaultdict(collections.Counter)
    seen = set()
    for d in load_jsonl(labels_path, require="category"):
        key = "%s:%d" % (d["kind"], d["pid"] if d["kind"] == "post" else d["cid"])
        if key in seen:
            continue
        seen.add(key)
        b = bucket_of(d)
        if b in ("V", "W"):
            c[b][d["category"]] += 1
    out = {k: round(_mix(c, n_v, n_w, k), 4) for k in CATS}
    out["of_subject_venue"] = round(out["venue"] / (out["venue"] + out["external"]), 4)
    out["n"] = len(seen)
    out["by_bucket"] = {b: dict(c[b]) for b in c}
    return out


def calibration(path=FROZEN / "calibration_generic_vs_specific.jsonl",
                specific=FROZEN / "trio_1f916_venue_specific.jsonl"):
    """How much of the answer is the wording rather than the corpus."""
    key = lambda d: "%s:%d" % (d["kind"], d["pid"] if d["kind"] == "post" else d["cid"])
    g = {key(d): d["category"] for d in load_jsonl(path, require="category")}
    s = {key(d): d["category"] for d in load_jsonl(specific, require="category")}
    both = sorted(set(g) & set(s))
    if not both:
        return None
    agree = sum(g[x] == s[x] for x in both)
    vg = sum(g[x] == "venue" for x in both) / len(both)
    vs = sum(s[x] == "venue" for x in both) / len(both)
    return {"n": len(both), "agreement": round(agree / len(both), 3),
            "venue_share_generic": round(vg, 3), "venue_share_venue_naming": round(vs, 3),
            "swing_points": round(100 * abs(vs - vg), 1),
            "sampling_se": round(math.sqrt(vg * (1 - vg) / len(both)), 3),
            "read": "the wording moves the level by an order of magnitude more than the sample "
                    "does, so no absolute level from this directory is publishable"}


def report(square, lemmy):
    cal = calibration()
    return {
        "predicate": "venue / external / none, no default clause; one prompt, both venues",
        "measured_at": "2026-08-31", "labels": "results/venue_conflation/",
        "square": square, "lemmy": lemmy,
        "gap_strict": round(square["venue"] - lemmy["venue"], 4),
        "gap_of_subject": round(square["of_subject_venue"] - lemmy["of_subject_venue"], 4),
        "published_comparison": {"square_venue_share": 0.4245, "platform": PLATFORM,
                                 "published_gap": round(0.4245 - PLATFORM, 4)},
        "calibration": cal,
        "read": "the ordering INVERTS: published, the square sits below its human comparator; "
                "measured symmetrically it sits above. lemmy also carries 3.6x the subjectless "
                "content, which a binary must assign silently and differently per venue. NOT a "
                "collapse finding -- a subject axis cannot separate recycling from a venue whose "
                "surface is expanding into checkable reality, which is what accreting a token, a "
                "witness file and an event log does. Read the TREND, and read depth "
                "(respecifiable / derived) for whether work could have come out otherwise.",
    }


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, str(REPO / "analysis"))
    cache = json.load(open(os.path.expanduser(
        "~/personal/memetic-workdir/allocation_label_cache_agent.json")))
    sq = venue_profile(FROZEN / "trio_1f916.jsonl",
                       lambda d: cache.get("%s:%d" % (d["kind"], d["pid"] if d["kind"] == "post"
                                                      else d["cid"])), 15186, 18146)
    lab = json.load(open(os.path.expanduser(
        "~/personal/memetic-workdir/allocation_labels_lemmy.json")))["lemmy"]
    lm = venue_profile(FROZEN / "trio_lemmy.jsonl", lambda d: lab[d["pid"]],
                       sum(1 for x in lab if x == "V"), sum(1 for x in lab if x == "W"))
    print(json.dumps(report(sq, lm), indent=1))
