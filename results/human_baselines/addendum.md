# Addendum — the corrected semantic finding: mostly register; the idea-level residual is unresolved

*An addendum to [`report.md`](report.md), correcting its **semantic-diversity** instrument (item-level
Vendi). Two solid corrections and one honest non-result. **(1)** The report's headline semantic gap
(agents ≈ 0.38× human diversity, a ≈ 2.6× gap) is **mostly writing register** — shown directly by a
register-transplant experiment. **(2)** What remains **at the level of ideas is comparator-dependent, and
both of the report's human comparators are confounded** (one is a permissive "discusses-everything" upper
bound and possibly part LLM-written; the other was mischaracterized as insular when it is structurally a
leaky bucket), so this instrument **does not cleanly establish an idea-level self-referentiality gap** —
in either direction. **(3)** The self-referentiality question, at the idea level, therefore **relocates
to topic/venue allocation** — how much of the community's discourse is self-focused — which is the domain
of the report's *self-reference-rate* instrument, not this one, and is left open here. Thread-dynamics
claims are retracted. This corrects the semantic instrument only. A separate exploratory "core-to-core"
comparison is **parked** (suggestive but confounded — see §3); it is not load-bearing. Numbers in
[`addendum_results.json`](addendum_results.json); `report.md` should link to this note.*

## 1. Most of the raw gap is register (established directly)

Vendi over *item* embeddings is unit-dependent, and the agents write in a few structured genres (audit,
receipt, manifesto); a sentence embedder can read that shared **register** as low diversity independent
of content. We identify register's effect directly, holding content fixed:

- **Register transplant.** Take the *same* diverse-human openings and run three arms: baseline; a neutral
  Qwen **pass-through** (restated in its own style — mediation noise only); and the text **rewritten into
  the agent register** (mediation + register). Pass-through barely moves Vendi (16.3 → 16.2 — mediation
  noise is negligible), but the agent-register rewrite collapses it **16.2 → 10.6 (−35%)**. Register is a
  genuine Vendi-suppressor at constant content.
- **Validated (with one caveat).** The claim-normalizer used below does unequal work (15.8 : 1 on agent
  text vs 1.6 : 1 on human). A round-trip — claim-normalize the register-transplanted text — recovers
  **95%** of the baseline claim-diversity, and a **per-item** check confirms content is *preserved*
  (cosine 0.82 to the original claim vs 0.41 random floor), not swapped. Caveat: the transplant and the
  normalizer are one Qwen model under fixed prompts, so the −35% is register *as Qwen imitates it* — a
  caricature could over- or under-state it. The pass-through controls mediation noise, not caricature.
- **Not a single-embedder quirk.** The full-text → claim recovery reproduces on bge, mpnet, and gte; a
  ≥3-author 8-gram rule removes ~0% of opening tokens, so the register is *structural*, not verbatim.

So the raw ≈ 2.1× (openings) / ≈ 2.6× (full corpus) deficit is mostly register. The question is what, if
anything, remains at the level of ideas.

## 2. The idea-level residual is comparator-dependent — and both comparators are confounded

Register-controlled (claim-normalized) Vendi is **not one number**; it depends on the human comparator,
and neither of the base report's comparators can carry the claim:

| agent / human, idea level (register stripped) | value (across 3 embedders) | why it's confounded |
|---|---|---|
| vs **diverse** forum (HN, whole) | 0.66 – 0.75 (≈ 1.3–1.5×) | a "discusses everything" **permissive upper bound** (the base report's own caveat); fresh 2026 content, possibly part **LLM-written** — bias of *unknown direction*, so not even a clean lower bound |
| vs **"insular"** forum (whole) | 0.76 – 1.12 (embedder-dependent) | **mischaracterized:** structurally a **leaky bucket** — a tiny persistent core (top-5 authors = 59% of content; the >5-year core writes 64%) around a large rotating cast of drive-by hobbyists (63% of authors <7-day tenure). "vs insular" compared agents to a **tourist-diluted blend**, not a cohesive insular community |

So the register-controlled semantic instrument **does not establish an idea-level self-referentiality
gap** — the vs-diverse deficit rides a permissive, possibly-contaminated baseline, and the vs-insular
comparison is against a mischaracterized corpus and is embedder-unstable (straddles parity). We can say
the raw gap is mostly register; we **cannot** cleanly say whether a real idea-level gap remains.

## 3. Where the self-referentiality question actually lives

The register-controlled semantic-diversity instrument, then, is largely silent on the base report's
construct. That is because **idea-*diversity* is the wrong level for "self-referentiality."** A community
can be perfectly idea-diverse *about itself*; what "self-referential" means is an **allocation** claim —
what fraction of the discourse is turned inward (governance, provenance, the treasury, agent-existence
meta-talk) versus outward. That is the domain of the report's **self-reference-rate** instrument, not the
Vendi instrument, and it is the honest place the question relocates to. We have **not** measured it here
(what share of the agents' *entire* discourse is self-focused, versus the equivalent share for a human
community's *total* output); that is the natural next measurement.

> **Parked exploratory note.** We ran a "core-to-core" comparison — the agents' most-active authors vs the
> sustaining cores of human communities, including a pre-LLM Usenet self-governance core — and found the
> agent core's register-controlled idea-diversity lands in the range of a human *governance* core. We are
> **not** treating this as a finding: it conditions on self-governance (the very trait under study), it
> compares an activity proxy against validated multi-year persistence cores, and it rests on a single
> post-hoc comparator with no equivalence test. It is kept as exploratory work, out of this correction.

## 4. Thread dynamics — retracted

The first draft promoted a thread-geometry finding ("agents converge tighter, not faster, and never
close"). It does not survive the controls: **tighter** was register (on register-stripped claims all
three forums open at the same distance and agents end only ~7% tighter); **"no closure"** is false at the
median (agent median thread = 4 items, ≈ the insular forum's 3); and **"dwell"** is not detected. "Not
faster" holds.

## What this changes in the base report

- **The semantic magnitude is register-inflated.** "≈ 0.38× diverse humans (≈ 2.6×)" is mostly register;
  the idea-level residual is comparator-dependent and unresolved by this instrument.
- **The idea-level self-referentiality claim is not established by the semantic instrument.** Neither
  human comparator can carry it; the question belongs to the allocation / self-reference-rate instrument.
- **Scope and a knock-on.** This corrects the *semantic* instrument only. The report's other instruments
  (self-reference rate, long-window perplexity) are **not** register-controlled here and should be treated
  as such until re-run — though a zstd-on-claims compression proxy still separates the agents somewhat
  after register-stripping, so the token-level story is *not* purely register. Separately, the base
  report's instrument self-validation (Finding 2) was built on the same whole-forum comparisons §2 shows
  are confounded, and no longer stands as written.

## Caveats

- The transplant and claim-normalizer are one Qwen model under fixed prompts (two method families, one
  mediating model); a second, unrelated model would strengthen the register attribution.
- CIs are subsampling noise only; the cross-embedder spread (e.g. 0.76–1.12 vs insular) is the honest
  uncertainty. Vendi is used only as ratios, never as absolute values across differently-embedded
  pipelines.
- The diverse baseline is fresh 2026 content of unknown contamination direction; the "insular" comparator
  is a leaky-bucket blend; a pre-2023 pull and a properly matched comparator would both help.
- Observational; no causal claim.

## Bottom line

Most of the raw semantic gap is **register** — put the agent house style on human content, unchanged in
substance, and its measured diversity falls by a third. Whether any **idea-level** self-referentiality
gap remains is **unresolved by this instrument**: both of the report's human comparators are confounded,
so the honest answer is "we can't say from Vendi." And that is partly the wrong tool — "self-referential"
is a claim about how much of the discourse is turned inward, which is a matter of **allocation**, not
per-item idea-diversity. That question is left open, and is where this line of work should go next.
