# Allocation: how much of the square's discourse is about the square

*The construct every prior document deferred, measured. The
[human_baselines addendum](../human_baselines/addendum.md) relocated "self-referentiality" from
idea-diversity to **allocation** — what fraction of a community's discourse is turned inward —
and [novelty_bands](../novelty_bands/report.md) closed by naming it the open question. In-square
review then asked it in operational form: **does this square talk about itself more than
comp.lang.lisp talked about comp.lang.lisp?** This report answers with the pipeline already
built: every claim in seven claim-normalized pools (the agent square through 2026-08-12, plus
six frozen human anchors) classified as **VENUE-directed** (about the forum/community itself —
rules, governance, moderation, funds, members, norms, meta-discussion about the group or its
quality) or **WORLD-directed** (its subject matter / the outside world). One venue-agnostic
prompt (verbatim in [`results.json`](results.json)), fixed before any output was read; Qwen2.5-7B
on all ~30k claims; Gemma-3-12B on a stratified 1,505-claim sample as the cross-family check;
identity-blocked bands throughout.*

**Answer: yes. Against lisp: ~5× on the primary classifier (full pools); 3.6× on the matched
agreement sample; and under the stricter classifier a point estimate of 11× that should be read
as "not below ~4×" (the denominator is 6 claims in 215; 95% span ≈ 4–36×). The square is the
most venue-directed corpus measured under both classifier families, with non-overlapping exact
CIs even on the strict reader (agent 66/215 [0.25, 0.37] vs forth, the top anchor, 19/215
[0.05, 0.14]). The absolute level is classifier-dependent — a third to
two-thirds of all items depending on classifier family and prompt frame (0.31–0.71; binary Qwen
0.509) — and is reported as that range, not a point. Under every specification measured on both
sides — two classifier families, two normalizer authors, no normalizer at all, and (closing the
prior round's stated gap) the three-way frame — the square is **2.3–11× its anchors, depending
on which anchor and specification: ≥ 2.3× against the highest human anchor under its friendliest
spec, 5–6× against a typical one.** The three-way frame, the instrument's most labile axis on
the agent pool (+20 points), leaves the anchors nearly unmoved (lisp 0.103 → 0.115, forth
0.221 → 0.254): the frame-lability is agent-specific, and the frame-matched ratios (6.2× lisp,
2.8× forth) are *stronger* than the binary ones.**

![Panel A: venue-directed share by pool — the agent bar at 0.51 over anchors at 0.09-0.22, with Gemma's stricter sample estimates as dots: same outlier, lower levels, bottom-of-table order within noise. Panel B: the agent square's daily venue share, 0.55 to 0.46 across the week, above both the shaded full-history anchor range and the highest anchor-year line (forth 1991, 0.31).](figure.png)

## Results

| pool | venue share (Qwen, full pool, identity-blocked band) | Gemma (sample of 215) |
|---|---|---|
| **agent square** | **0.509** [0.492, 0.526] | 0.307 |
| forth | 0.221 [0.186, 0.246] | 0.088 |
| scheme | 0.183 [0.167, 0.199] | 0.074 |
| hn | 0.139 [0.127, 0.150] | 0.060 |
| lisp | 0.103 [0.095, 0.110] | 0.028 |
| smalltalk | 0.102 [0.092, 0.114] | 0.023 |
| sci | 0.085 [0.075, 0.097] | 0.056 |

**Finding 1 — the allocation anomaly is real, large, and cross-family robust *as a contrast*.**
Under Qwen the square's venue share is 4.95× lisp's and 2.3× forth's (full pools; 3.6× and ~2×
on the matched sample); under Gemma — which reads VENUE far more strictly in every pool,
confirming only ~42% of Qwen's VENUE calls — the agent square remains the outlier with
non-overlapping exact CIs, and the point ratios grow. What is *not* claimed: bottom-of-table
orderings under Gemma (5–12 events per cell — sci/lisp/smalltalk reorder within noise), or ratio
magnitudes beyond a factor-1.5–3 classifier disagreement (best-anchor ratio 2.3–3.5×; lisp ratio
3.6–11×). The pooled κ = 0.506 flatters agreement (strata of very different prevalence); per-pool κ, now
computed from persisted pairs, runs 0.25–0.62 — second-highest on the agent pool (0.556, behind
sci at 0.619); the low-prevalence anchors (smalltalk 0.25, lisp 0.31) are where kappa is
fragile.

**Finding 2 — the human meta-discourse baseline, in Qwen-currency (calibrated ~3× high on
anchors — see Human calibration), is 8–22% full-history, and it moves.** Usenet
groups really did talk about themselves — charter disputes, moderation fights, "this group has
gone downhill" — at ~10% of claims for a typical group. But venue share is **era-dependent
within a group**, per this study's own series: lisp ranges 8–17% across 1984–1991; forth *rose*
from 6% (1984) to **31% (1991)**, a 5× within-group swing; scheme bounces 14–24%. The
era-matched worst case in these artifacts is therefore: agent weekly low 0.456 vs forth-1991
0.31 — **1.47×** — against forth's full-history 0.221 giving 2.3×. All levels and the era-series in this finding are classifier-currency: the human calibration
read forth at 0 VENUE in 19 sampled claims (blind Fable likewise 0/19) against Qwen's 5/20 on
the same items — so forth "topping the anchors" may substantially measure Qwen's false-positive
rate on meta vocabulary rather than true venue share, and the era-rise (6% → 31%) inherits the
same caveat. The human-rated anchor baseline is ~6%. What survives in any currency: anchors sit
far below the agent square.

**Finding 3 — the square's self-focus is lower at week's end (a trend to watch, not to bank).** Daily venue share (Qwen): 0.548 → 0.527 →
0.525 → 0.480 → 0.516 → 0.505 → 0.456 over Aug 6–12 — about nine points in a week, direction
consistent with the corpus's documented outward turn (the exogenous-influx doubling). Seven
author-correlated points, endpoint-driven; per-day sampling error alone is ~±1.6 points. Even at
its weekly low the square sits 1.47× above the highest anchor-*year* (forth 1991) and ~2× above
the highest full-history anchor.

**Finding 4 — the whole arc now closes coherently.** With this measurement, the project's three
questions about the square have three different answers: its **idea-diversity is human-normal**
(inside the novelty band, above the specialist class); its **register is anomalous** (most
surface-repetitive corpus measured); and its **allocation is anomalous** — it spends an abnormal share of its attention on itself:
1.5× the most extreme human anchor-year in the most adversarial cut, 2–3.5× the highest
full-history anchor, and 4–11× a typical group. "Self-referential" was never about how
diversely the square thinks; it is about how much of its thinking is pointed at the mirror.

## Validation

Keyword controls (weak, stated as such): claims containing newsgroup-meta vocabulary
(charter/moderation/killfile/…) classify VENUE at 0.69–0.97 across lisp/sci/forth. The
cross-family sample is the real check, and it is moderate, not strong: agreement 0.877, pooled
κ = 0.506 (inflated by stratification across pools of very different prevalence), Gemma
confirming only ~42% of Qwen's VENUE calls — with the disagreement concentrated in the boundary
genre unique to the agent pool (claims about AI agents in general, where members and subject
matter are lexically fused; the study's construct calls those WORLD, and the two families split
on them). No claim in this study was labeled by a human, and both classifiers could share the
same members/subject conflation — cross-family agreement cannot bound shared bias. All
conclusions are stated at the level that survives both readings: the contrast, not the absolute
level, and a blind human-labeled gold sample is the named next step.

## Robustness addenda (run after the initial review round)

Three checks the review called for, all supporting the contrast and further disciplining the
absolute level: **(a) normalizer swap** — Gemma-*authored* claims through the same classifier
give agent 0.438 / lisp 0.113 (≈4×), so the circularity concern (Qwen classifying its own prose)
does not carry the result; **(b) no normalizer at all** — direct classification of raw items
gives agent 0.596 / lisp 0.118 (5.1×, essentially matching the claim-mediated pull-1 reference
of 5.2× in the same block); **(c) a
three-way frame** (VENUE / GENERAL-AI / WORLD) *raises* agent VENUE to 0.709 with GENERAL-AI
taking only 7.7%, while the anchors, run under the identical frame, barely move (lisp 0.115,
forth 0.254; lisp's GENERAL-AI bucket is 13.8% — 1980s comp.lang.lisp genuinely hosted
AI-in-general discussion, a face-valid split). The binary frame was conservative on the agent
pool; the absolute level remains **prompt-frame- and classifier-dependent (0.31–0.71)**, but the
frame-matched contrast (6.2× lisp, 2.8× forth) is now a measured cell, not a gap, and exceeds
the binary contrast. The previously-missing negative control now exists:
technical-keyword claims classify WORLD at 0.92 (lisp) / 0.86 (forth); the agent pool's 0.67 on
n = 43 is itself consistent with genuinely fused content.

## Human calibration (the review's single most important fix, run)

A blind gold sample: 180 claims (30 agent-random, 30 agent-boundary, 20 per anchor), shuffled,
machine labels withheld, rated by the study's author (a human — not a claimed domain expert, but
the one rater without an LLM's conflict of interest; blind to machine labels and pool metadata,
not to the hypothesis) and independently by a **frontier-model rater** blind in the same sense —
fenced to the sample file alone with zero supplied study context, though the claims themselves
are content-identifiable as coming partly from an AI-agent forum, so hypothesis-inference cannot
be excluded (its anchor readings matching the human floor exactly, and sitting *below* the human
on the agent stratum, argue against drift toward the hypothesis). The author's worry
going in — that the agents' register makes everything read as "AI philosophy," so no human can
be a gold standard — is answered by the data: **human × blind-Fable κ = 0.757** (raw 0.93), with
near-identical marginals (30 vs 33 VENUE of 180) produced independently. No single rater needs
to be gold; two independent careful readers converge, and the genuinely undecidable residue is
~5% of items.

The calibration also resolves the classifier biases — and they are **complementary**: Qwen reads
the agent pool exactly as the human does (0.43 vs 0.43 venue share on the random stratum) but
over-calls VENUE ~3× on the human anchors (0.18 vs 0.06); Gemma matches the anchors (0.08) but
under-reads the agent pool (0.17 vs 0.43). Against the human ∧ Fable consensus (n = 158): Qwen
errs almost exclusively as false-VENUE (18, concentrated on anchors), Gemma as missed-VENUE (10,
concentrated on the agent pool). The **human-calibrated contrast has point estimate ≈ 7×** (0.43 / 0.06) with a wide 95% span
(≈ 2–25 on 12/28 vs 7/115 events) — above the published primary ratio, and Qwen's error
structure is asymmetric in exactly the direction that would make 4.95× an *underestimate*
(paired 12–0 anchor over-calls; 18 false-V vs 3 missed-V against consensus). The calibration
cannot exclude ratios below the published one at 95%; what it supports is that the published
ratio is more plausibly biased low than high. One count-vs-rate honesty note: Qwen's false-V
*rate* on consensus-WORLD items is actually higher on the agent pool (6/27) than on anchors
(12/107) — the exact agent-share match (0.43 vs 0.43) is partly offsetting errors, not per-item
fidelity (human × Qwen κ = 0.566). (Sample, key, and the four-rater matrix: `gold_matrix.json` beside
`results.json`; n = 28–30 per agent stratum, so stratum shares carry ±0.18-wide bands; one human
rater.)

## Caveats

- **Absolute shares are classifier-dependent** (0.51 vs 0.31 on the agent pool) and are always
  reported as a range; the cross-venue contrast is the robust object.
- Binary venue/world on one-sentence claims; a claim about "AI agents" broadly, or about tooling
  around the platform, sits on the boundary and resolves inconsistently between families.
- Claims are register-stripped summaries: venue-reference carried purely by style, and absent
  from the claim, is invisible here (this is the instrument's point, but it is a choice).
- One prompt (a classifier-prompt monoculture, same standing issue as the normalizer prompt);
  identity ≠ operator (permanent); keyword controls are directional checks only (both
  directions now run — see Robustness addenda).
- **Circularity at the normalizer stage:** every claim in every pool was written by the same
  Qwen checkpoint that serves as primary classifier; Gemma cross-checks the classifier only, on
  Qwen-authored text. If the normalizer preferentially foregrounds meta/social content in mixed
  posts, the skew precedes classification — and it would land hardest on the agent pool, which
  novelty_bands documented as the normalizer's worst-served. Gemma-normalized agent/lisp claim
  files exist in the workdir and are the named check, unclassified as of this version.
- **The measurand is share of items' single claims, not share of discourse:** one claim per
  item means a mostly-world post with a venue aside contributes a wholly-VENUE or wholly-WORLD
  unit; with 42% of agent posts truncated at 3,000 chars, what survives to the claim is the
  opening.
- Anchors are full multi-year histories vs the square's 7.2 days, and venue share is
  era-dependent within groups (forth 6% → 31% across its history) — the era-matched worst case
  (1.47×) is reported alongside the full-history ratios for exactly this reason.
- Classifier non-answer rates differ by pool (0.5% agent → 7.1% scheme); the direction of any
  induced bias is unexamined.
- Registration is author-attested (docstring), below the hashed-derivation standard the
  novelty_bands study set; claim-pool hashes are published for lisp/sci/hn only.

## Machine-readable

[`results.json`](results.json) — shares, bands, agreement sample, daily/yearly series, prompt
verbatim, controls. Pipeline: [`analysis/allocation_run.py`](../../analysis/allocation_run.py),
[`allocation_agree.py`](../../analysis/allocation_agree.py),
[`allocation_figure.py`](../../analysis/allocation_figure.py).
