# Novelty bands: placing the agent square on a human specialization axis

*Follow-up to [`results/human_baselines`](../human_baselines/report.md) and its
[addendum](../human_baselines/addendum.md). The addendum ended at an honest dead end: after register
control, the idea-level comparison was **comparator-dependent**, and both of the original human
comparators were confounded (one permissive and possibly LLM-contaminated, one a mischaracterized
leaky bucket). This pass replaces the single-comparator design with a **band**: multiple public,
pre-LLM human venues chosen to span topical breadth — from single-topic to broad — so the agent
community is *placed on an axis* rather than tested against one matched (and therefore arguable)
control. Bands, not parity.*

**Headline: on every register-controlled instrument, under two independent normalizer families and
three embedders, the agent square sits *inside* the human range — more idea-diverse than a
single-topic human community, less than broad ones. At the surface (raw-text) level it remains the
most repetitive corpus measured: the house-style register, as the addendum established.**

## 1. Design

The Usenet comparators were selected on **structure only** (volume, span, remit, membership
churn), before any novelty instrument was run on them, to avoid the forking-paths and
construct-matching failures the addendum documents. That blind-selection claim is scoped
honestly: it holds for the Usenet anchors but **not for HN**, which entered this band with
known (favorable-to-the-old-hypothesis) numbers from the base report — HN is retained as a
continuity anchor, and no conclusion below rests on it. These commitments are as-of-writing;
the repository's first commit of this directory is their registration timestamp. The unit of comparison is the **venue**: what a reader of that one forum saw.
The agents' venue is their entire public square; that asymmetry (one venue *is* the whole society)
is a design premise stated here, not an oversight — what fraction of a whole community's discourse
lives in one register of venue is the separate, still-open **allocation** question, and no result
below speaks to it. This report measures **idea-diversity and novelty**, not "self-referentiality."

| corpus | role | items | span | source |
|---|---|---|---|---|
| **agent** | the community under study | 2,874 | 73.5 h, Aug 2026 | 1f916.ai (`data/posts`) |
| **lisp** | single-topic pole | 5,721 | 1983-05 → 1991-06 | `net.lang.lisp` → `comp.lang.lisp`, UTZOO NetNews Archive |
| **sci** | broad pole, pre-LLM | 2,836 | 1984-06 → 1988-05 | `net.sci` → `sci.misc`, UTZOO |
| **hn** | broad pole, modern | 2,859 | 2026 pull | Hacker News API |

Every Usenet anchor is **public and reconstructible** (the UTZOO archive is on archive.org;
HN is reconstructible in kind, not item-for-item — its story-ID manifest is not published — and
is a non-load-bearing continuity anchor; the parse
rules — group directories as the reader's view, `Newsgroups:` header confirmation, Message-ID
dedup across double-stored tapes, quote/signature stripping, hashed authors — are in the analysis
scripts). The earlier study's insular phpBB forum is **retired from released comparisons**: it is
the one corpus a reader cannot obtain. Its numbers survive only in the already-published
human_baselines documents, where it appears generically.

Structure of the new anchors (churn/core signature, window = year, core = active ≥ 3 years): both
are open venues, not insular communities — top-5 authors hold 9% (lisp) / 5% (sci) of content,
~70% of authors are drive-bys, newcomer→core permeability 4–5%. The sci lineage is 62%
crossposted; a broad "general science" group on 1980s Usenet is partly a crosspost hub, and that
is accepted as what the broad remit *is* on that platform.

## 2. Instruments

Only the instruments that survived the addendum's register correction are used, in their corrected
form:

- **Claim-normalized Vendi ratios** — each item is reduced to a one-sentence core claim before
  embedding, stripping the register that dominated the raw comparison. Two **independent normalizer
  families** run the identical prompt: Qwen2.5-7B-Instruct (fp16, greedy) and Gemma-3-12B-it
  (llama.cpp, greedy). Three embedders (bge-large / mpnet / gte-large); matched subsamples
  m = ⌊0.8 × 2,836⌋ = 2,268 (80% of the smallest pool); ratios only, with the **cross-embedder ×
  cross-normalizer spread as the honest uncertainty**. Bracketed bands are item-subsampling noise
  only, *not* author-clustered, and on the agent side m/N ≈ 0.79 means successive subsamples share
  most of their items — the bands understate true sampling uncertainty and are treated accordingly
  (conclusions are stated at their minimum cell). An **identity-blocked** bootstrap of the load-bearing
  agent/lisp cell is **[1.244, with 90% band 1.192–1.289]** — blocks are the platforms' own
  identity labels (1f916 author names; hashed Usenet addresses), each identity clustered only to
  itself. What that corrects is **within-identity** dependence, and nothing more. The true
  independence unit is the *operator*, and identity ≠ operator on both sides of the ratio: one
  operator may run several agent personas (and personas share model lineages), one 1980s user
  posted from several addresses. Identity-level blocking therefore understates the real
  clustering — and the gap is **uncorrectable by design**: discovering the true unit is identity
  linking, which this project's data-governance covenant forbids. Operator-level dependence
  stands as a permanent caveat, not a solved problem. (Computed at bge; the minimum headline
  cell, gte, is not blocked — a further stated limit.)
- **Rolling claim-Vendi / W** (120-item windows) — the maturity-controlled variant.
- **zstd conditional novelty** (level 19, 512 KB window), computed uniformly on all corpora, on
  **raw text** (verbatim recycling) and **on claims** (idea recycling), aggregate ratio at matched
  N = 2,836. This uniform pass supersedes the base report's per-forum zstd cells, one of which
  (diverse forum, 0.745) proved not exactly reproducible from its stored control metrics.
- **Normalizer validation, in-regime** (the addendum's §1 standard, run for *both* normalizers on
  *these* corpora): per-item content preservation vs a shuffled floor, degenerate-claim audit,
  compression-work ratios. Both models pass on all pools; lisp — the pool where a code-collapse
  artifact would fabricate the headline — has the **highest** preservation of any corpus under both
  models (0.78 vs floors ≈ 0.55), with duplicate-claim rates ≤ 0.7%. The two families also
  independently surface the same most-recurrent lisp claim (the Common-Lisp-vs-EuLisp dispute).
  The same table cuts the other way and that is stated plainly: the **agent corpus is the
  worst-served pool** (preservation median 0.65–0.66, the smallest margin over its floor), its
  items do the most compression work (11–12:1 vs 3:1 for HN), and the 3,000-character input
  truncation touches ~42% of agent *posts* — so one-claim-per-item flattening falls hardest on
  the agent corpus. The **direction** of that instrument error is not assumed: template-like
  normalization failures *deflate* claim-diversity, but noise-like or over-specific failures
  *inflate* it (spread-out embeddings are what Vendi rewards), and low preservation alone does not
  say which mode dominates. Two empirical checks rule out the template-collapse error mode (the inflation mode — noisy or
over-specific claims spreading the embedding cloud — is bounded only loosely, by agent claim
genericity landing at human-anchor levels; stated as such). **Truncation stratification**:
  restricting the agent pool to items untouched by the 3,000-char cut leaves agent/lisp at 1.261
  [1.227, 1.285] versus 1.254 for the full pool — truncation does not drive the result.
  **Genericity audit** (mean claim-to-claim cosine across *different* items): agent claims 0.496,
  *below* lisp's 0.538 and level with forth's 0.494 — the normalizer is not collapsing agent
  items into generic near-identical claims; and the raw-text version of the same statistic is
  *highest* for the agent corpus (0.672 vs 0.626/0.663), which is the register story again —
  agent raw text is the most mutually similar, agent claims are not. The residual caveat is the
  "below the broad pole" half: agent < sci/hn may still be partly instrument (one claim per item
  flattens multi-claim agent posts), and that half is stated with less confidence. The validation also does not check injectivity (a normalizer
  mapping distinct ideas to generic near-identical claims would pass it); the duplicate/near-dup
  audit bounds the grossest form of that failure but not subtler genericity.

Usenet thread-roots are treated as posts (subject + body), replies as comments (body only),
mirroring the other corpora. Items under 20 characters are dropped everywhere — that filter is why
the agent corpus is 2,874 items here versus 2,890 elsewhere in this repo. For the zstd matched-N
cells, per-seed spreads are in `results.json`; note that for corpora barely larger than N = 2,836
(agent, HN) the five seeded subsequences are ~99% identical, so those cells carry essentially no
seed noise and their stability should not be over-read — the informative spread is lisp's
(0.694–0.710 raw).

## 3. Results

![Panel A: agent/comparator claim-Vendi ratios across three embedders and two normalizers — all lisp cells above parity, all sci and HN cells below. Panel B: zstd novelty positions — on claims, lisp recycles ideas more than the agents; on raw text the agents are lowest.](figure.png)

**Idea level (claim-Vendi, agent / comparator):**

| vs | bge (Q / G) | mpnet (Q / G) | gte (Q / G) |
|---|---|---|---|
| lisp (single-topic) | 1.26 / 1.32 | 1.27 / 1.22 | 1.08 / 1.13 |
| sci (broad, pre-LLM) | 0.67 / 0.76 | 0.67 / 0.60 | 0.77 / 0.81 |
| hn (broad, modern) | 0.62 / 0.72 | 0.57 / 0.55 | 0.73 / 0.80 |

**zstd novelty (matched N; lower = more recycling):**

| | raw text | claims (Qwen) | claims (Gemma) |
|---|---|---|---|
| lisp | 0.704 | **0.580** | **0.500** |
| **agent** | **0.644** | 0.614 | 0.551 |
| sci | 0.706 | 0.658 | 0.583 |
| hn | 0.714 | 0.690 | 0.591 |

**Finding 1 — one ordering, everywhere it was looked for.** `lisp < agent < sci ≤ hn` holds in
all six normalizer × embedder combinations of the claim-Vendi, in the rolling claim-Vendi under
both normalizers (0.108 / 0.135 / 0.162 / 0.191 and 0.084 / 0.110 / 0.119 / 0.138; rolling is
computed on bge only), and in zstd-on-claims under both normalizers. To be precise about what
replicates what: these are **one claim pipeline read three ways** (pooled diversity, windowed
diversity, compressibility), replicated across two normalizer families and three embedders — not
three independent instrument families. The zstd-on-claims view in particular partly re-measures
topical vocabulary narrowness (one-sentence claims about one topic share nouns), so it is a
secondary, not independent, confirmation. The genuinely independent axes are the normalizers and
embedders. And the vocabulary concession extends to the **Vendi cells themselves**: sentence
embedders cluster by shared vocabulary too, so claims about one language tighten the similarity
kernel partly because they share that language's jargon — since the anchors were *selected by
remit breadth*, part of any agent-vs-narrow-venue gap restates the selection variable.
"Idea-diverse" in this report should be read as substantially **topical breadth of the idea
space**; a venue whose *within-topic* idea space had collapsed would look identical on these
instruments, and no within-topic decomposition is attempted here.

**Finding 2 — the agents are more idea-diverse than the single-topic human anchor.** Every
agent/lisp cell is above parity (range 1.08–1.32) with its entire subsampling band above 1; the
minimum across all uncertainty axes (gte × Qwen, band floor 1.072) still clears it. The
single-topic human group also *recycles* ideas more than the agents (zstd-on-claims 0.580 vs
0.614 Qwen; 0.500 vs 0.551 Gemma). Because this is the load-bearing edge of the band and its
worst-case margin is ~7%, it cannot rest on one comparator — item-level subsample bands say
nothing about *anchor-level* sampling (lisp could be a lucky draw from its class of venues; its
decade-long CL-vs-EuLisp standards dispute is exactly how it might be). The comparator **class**
is owned as a construct definition, not a sampling convenience: the *typical mid-size specialist
venue* — a single-language `comp.lang.*` lineage with 2,500–8,000 merged raw articles, alive at
the archive end. That window has pre-outcome provenance: it is the criterion that selected lisp
in the first place (chosen to minimize researcher degrees of freedom, before any instrument ran),
and it is what keeps the class scale-comparable — a metropolis like `comp.lang.c` (48.6k
articles, ~11,800 authors vs the agents' ~340) differs from the agents on author-pool size alone,
which pumps measured diversity regardless of remit. The full sampling frame is published by an
**executable enumeration** ([`analysis/usenet_enumerate_anchors.py`](../../analysis/usenet_enumerate_anchors.py)):
thirteen single-language lineages in the archive, of which **ten** fall inside the class window
(including lisp and the erroneously-omitted perl — see the disclosure below) and **three** sit
outside it (c, c++, postscript: scale regime; c++ additionally set aside by a documented
pre-outcome decision). Sizes come from the script; the window classification itself is applied
in prose and in the hashed rule string — the script emits the uncapped frame. Nothing is hidden,
and out-of-class venues remain available to anyone as robustness targets. The lucky-draw question is
then answered by **replication, not census**: three anchors drawn at random from the non-lisp
class members as enumerated at draw time, seed derived by hashing the rule text
(`int(sha256(rule)[:8], 16)` = 704253817). The full derivation — the byte-exact hashed string,
seed, and draw — is published and executable at
[`analysis/anchor_draw.py`](../../analysis/anchor_draw.py); it is published for *checkability*,
not claimed as pre-registration (it was authored by the analyst mid-session). The draw produced
**forth, scheme, smalltalk** — an unfriendly draw, as it happens: forth and smalltalk are the two
famously insular-evangelist communities in the class. **Disclosed enumeration error:** at draw
time the class was believed to have eight non-lisp members; a post-hoc adversarial audit found
`comp.lang.perl` (5,348 articles) inside the window, making the true population nine. The
executed draw is **not re-rolled**: its results had already been read, and re-randomizing a draw
after outcomes are known is an inadmissible post-hoc alteration (forking paths) regardless of
motive — particularly when proposed by a related-party auditor (the reviewer shares a model
family with the analyst). The draw stands as executed over the population-as-enumerated; perl is **disclosed, not
measured** — measuring an anchor discovered after the verdict was read would extend the analysis
under the guise of repairing it. It remains runnable by any reader from the published pipeline (corpus builder →
`claimify_anchors.py` → class test), and is a natural first target for community-nominated
reruns. Criteria, numeric, fixed **before any anchor ratio was read** (author-attested —
see the process note below): *(replication)* lisp is judged not-lucky if ≥ 2 of the 3 drawn anchors show agent/X > 1
on the majority of embedders; *(strong form)* "more idea-diverse than the typical specialist
venue class" requires all four anchors above parity **on the median subsample ratio** (bands and
their crossings reported alongside — forth's bge band floor is 0.99); *(placement)* the inside-the-band headline
fails only if the agents fall below **all four**. Anything between is reported as interleaving —
inside the band, anchor-dependent at the edge. Two fairness views accompany the pooled ratios,
both computed on full contiguous corpora (no anchor is subsampled): per-anchor **rolling
claim-Vendi/W** (contiguous 120-item windows — the maturity-fair view, since pooled sampling
hands a decade-old venue its full topic drift against 73 hours of agent discourse) and the
author-blocked bootstrap of §2. Process note: the study's author selected no anchor and holds no
per-anchor expectations; the analyst was *not* blind (lisp's result was known when the class was
formalized), which is why the defense rests on pre-outcome provenance, published enumeration, and
a seed that cannot be rerolled — not on blinding.
**Result: replication passes at 3/3 drawn anchors, and the strong form at 4/4 — all twelve
anchor × embedder cells above parity** (correlated cells: three embedders re-read the same
claims, so this is four comparisons under shared normalizer error, not twelve independent tests;
forth's bge item-subsample band crosses parity, [0.99, 1.04]) (lisp 1.25/1.27/1.08, forth 1.01/1.08/1.02, scheme
1.21/1.31/1.07, smalltalk 1.24/1.34/1.07 on bge/mpnet/gte). Forth is reported for what it is:
near-parity (1.01–1.08), the closest venue to the agents' idea-concentration in the class — and
under the identity-blocked view its band crosses 1 ([0.90, 1.14]) — while scheme and smalltalk
replicate lisp's margin. The rolling (maturity-fair) view agrees: the agents' windowed
claim-diversity (0.135) exceeds all four anchors' (0.108–0.127). Lisp was not a lucky draw; the
agent square sits at or above the typical mid-size specialist venue class.

**Finding 3 — the surface-register residual is real and stays.** On raw text the agents are the
most repetitive corpus measured (0.644 vs 0.704–0.714 for the three human corpora). Direction
only: the three human values landing within 1.4% of each other suggests the instrument saturates
on ordinary human text at this level/window, so no precision is claimed for the human side beyond
"clearly above the agents." Registered as expected: the addendum showed this layer is house
style, and claim-normalization removes most but not all of the agents' deficit.

**Finding 4 — the broad pole is era-stable.** Pre-LLM general-science Usenet (1984–88) lands at
the same end of the band as 2026 Hacker News (claim-Vendi points 41.1 vs 44.0 on bge/Qwen; the
mpnet gap is wider at ~15%). This is **consistent with** breadth of remit, not era or platform,
setting the diverse end — stated as a consistency observation, not a causal claim: it is one
venue per era, and the HN corpus is mechanically breadth-favoring by construction (front-page
feeds, per-story comment caps, link-post bodies that are little more than URLs — its 3:1 work
ratio means HN cells are barely register-normalized at all). What matters for this report is
narrower and safe: the band's load-bearing anchors (lisp, sci, and the whole 13-anchor
population) are pre-LLM, so the HN contamination caveat does not touch the conclusions.

## 4. Reading

At the level of ideas, the agent square currently behaves like a **specialist human venue** —
broader than a one-language community, narrower than a general-science one. That is not the
signature of **venue-level idea-collapse**; whether the *society* is healthy is a different
construct that this venue-to-venue design cannot license a verdict on (it depends on allocation
and trajectory, both unmeasured here). What remains distinctive is (a) the surface register, and (b) the
unmeasured allocation question: a whole society whose single square has the topical breadth of one
specialist forum. The band also makes the methodology **repeatable**: the human anchors are frozen
archives, so each future corpus pull is claim-normalized and placed on the same axis — drift
toward the lisp pole means the square is narrowing; toward sci, broadening.

## 5. Third-normalizer replication

A third normalizer — Qwen3.6-27B (Q4, llama.cpp, thinking disabled), a different generation and
scale from either model above — was run on the agent and lisp pools with the identical prompt.
Stated in the design before the run (author-attested; registration timing is a publication
decision outside this document): the result is reported here whatever it shows. It shows agent/lisp =
**1.369 [1.336, 1.402] (bge), 1.140 [1.106, 1.181] (mpnet), 1.121 [1.109, 1.138] (gte)** — all
three cells above parity, with the bge value the strongest any normalizer produced. Finding 2
therefore holds in all nine normalizer × embedder cells — but the multiplicity is stated
honestly: the three normalizer models span only **two model families** (Qwen3.6-27B shares
lineage with Qwen2.5-7B), so the independent-normalizer count is 2, and all three share one
prompt, which remains a monoculture (see Caveats). Grid-wide worst cell: 1.083 (gte × Qwen2.5),
subsample band floor 1.072.

## 6. Caveats

- Subsample brackets are item-sampling noise only; **no number here is author-clustered**, and
  items by one author are not independent. The honest uncertainty is the cross-embedder ×
  cross-normalizer spread, which is why conclusions are stated at their minimum cell, not their
  mean.
- Two normalizer families, **one prompt**: prompt-level idiosyncrasy ("state the core claim in one
  sentence") is uncontrolled. The register-transplant result in the addendum also remains
  single-model.
- UTZOO is a partial feed (inflates churn estimates); the sci lineage ends 1988; lisp bodies
  include code (the in-regime validation bounds, but does not eliminate, differential normalizer
  behavior).
- Posting density differs enormously (73 hours vs. years); rolling windows control corpus age, not
  density.
- Two unquantified channels sit on the load-bearing edge and are answered empirically rather than
  argued: **quote echo** (1980s quoting was heterogeneous; residual parent text in a Usenet reply
  yields a claim faithful to its own item yet duplicating another item's claim — invisible to the
  preservation check, deflating lisp specifically) and **thread composition** (within-thread
  claims cluster by construction; thread-length distributions differ; the agent side's own
  quoting is un-stripped, so the net direction is unknown). Thread composition is answered empirically: the thread-blocked resample is 1.243
  [1.192, 1.292], indistinguishable from the item-level cell (thread labels are structural, not
  identity-derived). Quote echo is **not** cleanly
  answered and stands as a caveat: a roots-only cell was computed (1.572 [1.523, 1.657]) but is
  **withdrawn as evidence** — 47% of lisp items classify as thread roots, which is not a credible
  root rate (1980s mail gateways routinely dropped References headers), so that pool contains
  misclassified replies and the cell cannot isolate the channel it was built to isolate. The
  channel's plausible direction (residual parent text deflates lisp claim-diversity) would bias
  *against* the agents' measured advantage, but that is a direction argument, not a measurement.
- Observational; a placement, not a causal claim; and — stated once more — **not** a measurement of
  self-referentiality, which lives in allocation and is future work.

## Machine-readable

[`results.json`](results.json) — corpora, structure signatures, all Vendi/zstd cells, validation
numbers, parameters. Figure source: [`analysis/novelty_bands_figure.py`](../../analysis/novelty_bands_figure.py).
