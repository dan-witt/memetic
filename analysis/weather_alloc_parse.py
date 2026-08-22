#!/usr/bin/env python3
"""How the allocation classifier's raw answer becomes a V/W label — single source of truth.

Issues #1-#7 published a STRICT parse: a label is kept only when the answer starts with "VENUE"
or "WORLD". Issue #7 characterised what the discarded answers actually are. Re-running the frozen
prompt over all 83 uncovered items returned the same string 83 times out of 83: `SUBJECT MATTER`
— not a refusal and not garbage, but the second branch of the question the prompt itself asks
("...or about its SUBJECT MATTER or the outside world?"), echoed back instead of the one word the
prompt demands. The failure is therefore deterministic (greedy decoding), one-sided (every one is
semantically WORLD), and its effect on the published series is signed: dropping WORLD answers
inflates venue share. Issue #7 pre-registered adopting a corrected parse in issue #8.

Three parses, in increasing order of what they accept:

  strict    — the published currency of issues #1-#8. Starts with VENUE / WORLD.
  relaxed   — also accepts an answer that names exactly one of the two words anywhere. Note this
              recovers NOTHING from the observed failure mode: "SUBJECT MATTER" contains neither
              word. It is kept because it is the parse a reader would first propose, and showing
              it recovers zero is what motivates the third.
  corrected — also accepts the OBSERVED verbatim second-branch echoes as WORLD.

WORLD_ANSWERS is a list of strings this pipeline has actually seen, deliberately not a pattern.
A new failure string must be observed and added here; matching "subject" or "world" speculatively
would be a different classifier rather than a parse fix, and would silently change the currency.

Adopting `corrected` moves every day at once, so both series are published side by side and the
strict series stays the cross-issue currency (see the weather report's allocation caveats).
"""

# verbatim answers observed from the frozen prompt that unambiguously choose its second branch
# ("...or about its SUBJECT MATTER or the outside world?"). Upper-cased, stripped, as compared.
WORLD_ANSWERS = frozenset({
    "SUBJECT MATTER",
    "SUBJECT MATTER.",
    "THE OUTSIDE WORLD",
    "OUTSIDE WORLD",
    "THE SUBJECT MATTER",
    "SUBJECT MATTER OR THE OUTSIDE",   # 6-token truncation of the full second branch
    "SUBJECT MATTER OR THE",
})


def strict(w):
    """The published parse of issues #1-#8. `w` is the raw answer, stripped and upper-cased."""
    return "V" if w.startswith("VENUE") else "W" if w.startswith("WORLD") else None


def relaxed(w):
    """Accept an answer naming exactly one of the two words anywhere; the earlier one if both.

    An answer naming BOTH is still a refusal to choose and stays unlabelled unless one clearly
    leads. No stemming, no synonyms, no paraphrase matching.
    """
    iv, iw = w.find("VENUE"), w.find("WORLD")
    if iv < 0 and iw < 0:
        return None
    if iv < 0:
        return "W"
    if iw < 0:
        return "V"
    return "V" if iv < iw else "W"


def corrected(w):
    """strict, then relaxed, then the observed verbatim WORLD phrasings. Issue #8's parse."""
    return relaxed(w) or ("W" if w.strip() in WORLD_ANSWERS else None)


PARSES = {"strict": strict, "relaxed": relaxed, "corrected": corrected}
