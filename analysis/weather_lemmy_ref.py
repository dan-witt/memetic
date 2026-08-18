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


if __name__ == "__main__":
    print(json.dumps(levels(), indent=1))
