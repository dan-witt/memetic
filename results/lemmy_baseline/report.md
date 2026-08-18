# The lemmy.world founding baseline — the self-reference contrast, re-measured against a matched human founding

**Headline.** Measured against the first human comparator matched on velocity, self-organization,
and undifferentiated platform structure, the agent square's self-referential (VENUE-directed)
share is **not established above** the human platform's in any framing: in none do both classifiers
place it above, and in one they agree it is below. On the full 30 days they disagree in sign — Qwen
1.08 [1.03, 1.14], Gemma 0.66 [0.61, 0.71] — so that comparison is inconclusive in the strict
sense: the instrument contradicts itself and the envelope spans parity. On the
velocity-matched arrival window the disagreement narrows and the direction resolves downward; at
≥400 characters both classifiers place the square *below* the platform (envelope [0.51, 1.00]).
The contrast that holds in one direction throughout is against *topic-remit* communities
(envelope 1.42–2.38×) — a weaker and more specific claim than previously reported. The previously
published multiple rests on a comparator class we now argue is the wrong one — an undifferentiated
founding platform measured against single-topic Usenet groups. No arithmetic error was found in the
prior number; what changed is the choice of comparator — and that change is now measured rather
than argued.
Usenet's platform-level governance did live in dedicated groups: `news.groups` scores **0.755**
against `comp.lang.lisp`'s 0.103, and against **0.757** for lemmy's `c/newcommunities`, the
functionally identical venue forty years later (§7.3).

Every load-bearing number below carries an interval, and every allocation cell is measured by two
classifiers. Four states are distinguished throughout, because "the envelope spans the null" can
mean two quite different things:

| the two classifiers' intervals       | reading                                                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------------------- |
| both span the null                   | **indistinguishable** — no difference detectable, and at these n's not for want of power |
| disjoint, opposite sides of the null | **inconclusive** — the instrument contradicts itself                                     |
| disjoint, same side                  | **direction established, magnitude unresolved**                                          |
| one spans the null, one excludes it  | **not established** — the weaker classifier governs; at most a direction suggested by one of two |
| overlapping, both excluding the null | **resolved**                                                                             |

The cross-classifier envelope — the union of the two intervals — is the honest interval to quote,
but it is derived: it cannot separate the first two rows, so the state is named before the
envelope is given.

Instruments outside §6 report a single interval rather than two, and there "spans the null" splits
the same way: **indistinguishable** if the interval is narrow relative to effects worth detecting,
**unresolved** if it is wide enough to contain them. The distinction is not cosmetic — §7.1's zstd
cell and its perplexity cell both concern novelty, and only one of them is entitled to say the
corpora do not differ. Intervals that span their null are flagged inline and discussed rather than
buried.

**Stance.** This is a measurement, published for the measured. We hold no prior on whether the
square is healthy, and nothing here is scored as favourable or unfavourable to it — where a caveat
has a direction, we say which way the estimate would move and what would be **interesting** to
learn, not which side it helps. Several results below are unflattering to the instrument rather
than to either community, and that is the most useful kind we have.

---

## 1. Why lemmy.world, and what makes it rare

The allocation study's open question was whether the square's high VENUE share is an artifact of
being new. Answering that needs a human community whose founding can be *observed* and compared
against its own later state. Every previous candidate failed on one axis or another:

| candidate                                    | self-organizing                               | founding observable            | velocity at founding            | verdict                                               |
| -------------------------------------------- | --------------------------------------------- | ------------------------------ | ------------------------------- | ----------------------------------------------------- |
| `comp.lang.*` Usenet anchors                 | partly                                        | pre-1981 foundings unavailable | ~1–5 items/day                  | too slow, mostly no founding                          |
| `comp.lang.scheme` (founded in-archive 1987) | yes                                           | yes                            | ~1/day                          | n≈10 in a matched window — no power                   |
| wikipedia-l (2001)                           | yes                                           | yes                            | 3.05/day, 921 posts in 302 days | ~280× too slow                                        |
| Hacker News (2007)                           | **no** — benevolent dictatorship              | yes                            | ~160/day                        | venue-directed traffic is complaint, not constitution |
| reddit (2005)                                | no — editorially run, seeded with sockpuppets | yes                            | no comments until Dec 2005      | no discourse text at founding                         |
| Digg (2004)                                  | no                                            | **no** — API dead since 2012   | —                               | no archive exists                                     |

**lemmy.world is the only case that clears all three bars simultaneously.** Instance created
**2023-06-01 07:01:46 UTC**; users create their own communities and write their own rules
(`community_creation_admin_only = false`); and the reddit API exodus drove it from 3 communities
to 5,000 in 23 days, peaking at **5,979 items/day** against the square's ~1,000/day. It is a
high-velocity, self-organizing, from-scratch founding with the whole thing on the public record.

That combination is rare because it is close to self-contradictory: human venues that are born
fast are born fast *because something happened*, and the something is usually venue-related. In
human data, founding velocity and venue-neutrality are anticorrelated. lemmy.world's exodus origin
is therefore not an incidental blemish — it is the reason the corpus exists at all, and it is
handled by tiering (§5) rather than pretended away.

**The founding has two defensible day-zeros**, and we report both throughout:

- **06-01** — instance creation, the exact structural analogue of the square's day 0. Its first
  9.22 days carry only 1,705 classified items (**185/day**, against the square's ~995). It is not
  a clean pre-arrival window either: **67% of its items land on or after 06-09**, so it mixes the
  genuine ramp (561 items over 7.7 days, **73/day**) with the first two days of the influx. It is
  discounted for exodus contamination as much as for velocity.
- **06-09** — the exodus arrival, when community creation steps from 20/day to 166/day. Closer to
  the square's regime than 06-01 is, but **not matched to it**: this window carries 3,837 items/day
  against the square's ~1,000, so it overshoots by 3.8× where 06-01 undershoots by 5.4×. Day 0 is
  also an influx, not a founding. (On the truncated corpus this window read ~2,060/day and was
  described as velocity-matched; recovering the missing comments nearly doubled it.)

Neither is a perfect match and they do not always agree. Reporting one without the other would be
a choice dressed as a measurement.

## 2. The corpus

**Frame (pre-arrival cohort).** All local communities created **strictly before 2023-06-09 00:00
UTC** — i.e. before the migration step begins. **57 communities.** The boundary is chosen so the
exodus is an exogenous shock to a *fixed* set of communities rather than a mixture of pre- and
mid-wave foundings.

**Content window.** All posts and comments published 2023-06-01 07:01:46 → 2023-07-01 00:00 UTC.

Two frame details that differ between code and prose, neither with a numeric effect on this corpus
but both material to a re-pull. The crawler's community cutoff argument was `2023-06-09T07:01:46Z`
rather than the stated 00:00 — it holds only because no community was created in the gap (last is
06-08 23:47). And `lemmy_corpus.py`'s META set names **seven** communities; only the four discussed
here (`c/newcommunities`, `c/lemmyworld`, `c/fediverse`, `c/mastodon`) have any items. `c/mastodon`
is itself arguable: its remit is a *different* platform, which is one instance of a general problem
— on a federated network the VENUE boundary is genuinely fuzzy, and the Beehaw example in §9(b)
counts another instance's governance as venue-directed discourse here.

|                                              | value                                                       |
| -------------------------------------------- | ----------------------------------------------------------- |
| items                                        | **63,985** (5,585 posts + 58,400 comments)                  |
| items clearing the ≥20-char filter           | 55,223 (86%)                                                |
| authors                                      | 13,403                                                      |
| communities represented                      | 52 of the 57 framed                                         |
| median item length (≥20-char subset)         | 134 chars (topic tier 137; **agent square 1,376**)          |
| locally-authored                             | 58% (remainder federated in from other instances)           |
| span                                         | 2023-06-01 .. 2023-06-30                                    |
| square-matched arrival window (06-09 +9.22d) | **30,840 clearing ≥20 chars vs the square's 9,170 — 3.36×** |

**Composition, stated up front because it carries the headline.** The framed corpus is **55.7%
meta-tier**, and `c/lemmyworld` alone is **41.7%** of it (23,004 items). That is a property of the
frame, not of lemmy.world: the pre-arrival cohort is precisely the set that contains the
admin-founded governance communities while excluding the thousands of topic communities created
during the exodus. Relative to lemmy.world as a platform, this frame therefore over-weights the
meta tier, which makes the human benchmark more self-referential and the square correspondingly
less anomalous. Direction known, magnitude not. §5 argues the whole-platform mix is nevertheless
the right comparison; the alternative is to choose tier weights, which is a researcher degree of
freedom that can produce any answer wanted.

Records are built into the canonical anchor shape (`group / author / ts / msgid / root / subject /
text`) so every existing instrument consumes them unmodified. `root == msgid` marks a thread root.
Markdown blockquotes are stripped with **markdown-it**, a real CommonMark parser, locating
blockquote blocks by source line range — the markdown analogue of `strip_body()` on the Usenet
side. Authors are pseudonymized at ingest (SHA-1 of the ActivityPub actor URI, truncated).

Every record carries its **`ap_id`** — the globally unique ActivityPub URI — so any published
frame is verifiable against any instance in the federation without re-crawling lemmy.world.

**Acquisition.** `analysis/lemmy_crawl.py`. One request per **60 seconds**, taken from
lemmy.world's own `robots.txt` `Crawl-delay` rather than hardcoded, with every URL re-checked
against robots via `urllib.robotparser` before issuing. Identifying User-Agent. 891 requests over
~15 hours; per-community completion reasons recorded. `/search/` and
`/modlog` are `Disallow`ed and were not touched — note that `/modlog` is the single most
concentrated record of venue-directed governance activity on the instance, and it is off-limits.

Three acquisition defects were found and corrected, all of which silently under-collected:

1. **Federated backfill pollution.** `sort=Old` on the post endpoint returns items published
   2022-05 and 2022-11 — remote posts carrying their original timestamps, predating the instance.
   Filtered by `published >= T0`.

2. **Pinned posts sort ahead of `sort=Old`.** A community whose pinned post postdates the content
   cutoff would terminate its walk at *zero records* and log a clean completion. Fixed so only
   unpinned rows — which are genuinely ascending — may end a walk. `c/fediverse` was truncated at
   48 posts by this bug; its true count is 156.

3. **A pagination ceiling on the community-comment listing**, found by cold review after a first
   pass of this report had been drafted, and the largest of the three by far. The listing caps at
   ~page 101, right-truncating `c/lemmyworld` at 2023-06-12 and `c/selfhosted` at 2023-06-19 —
   5,000 comments each — while logging clean completions. The loss was **differential**:
   `c/lemmyworld` carries a ~0.65 VENUE share, so the truncation removed meta-tier mass
   specifically. It suppressed that community by 78% (4,919 items captured against 23,004 actually
   present) and the corpus as a whole by 38%. Repaired by a per-post comment sweep
   (`analysis/lemmy_crawl_repair.py`, 985 posts, +23,689 comments); nothing captured was deleted,
   and the repair is verifiably additive — all 40,296 originally captured items are present
   verbatim in the 63,985-item corpus.
   
   **Every number in this report is measured on the repaired corpus**, with two exceptions that are
   labelled where they appear: the LM perplexity cells (§7.1) and the gold sample (§8.2). The first
   pass measured the truncated corpus; the direction of the correction is that the human platform's
   venue share rose (Qwen 0.397 → 0.467, Gemma 0.342 → 0.417) and every agent-over-platform ratio
   fell. Where a first-pass number is quoted for comparison it is marked as such. The pagination
   caps themselves are recorded in `results.json` under `corpus.pagination_caps`, so the defect
   remains visible in the emitted data rather than only in this prose.

## 3. Data availability

**We are not distributing a corpus tarball.** The content is user-generated posts by identifiable
natural persons in the EU and elsewhere; redistribution raises GDPR obligations we are not
positioned to discharge, and the copyright in individual posts rests with their authors, not with
lemmy.world and not with us. Pseudonymizing author identifiers does not resolve either issue, and
the fact that ActivityPub replicates content by design is an argument about *protocol intent*, not
a licence.

We are working out how to publish a **dehydrated source** — a frame of `ap_id`s plus the parse and
normalization rules, sufficient to reconstruct the corpus without us shipping the text. Until that
exists:

- **We would rather share data than have anyone re-crawl the instance.** If you are reproducing or auditing this work, ask. 
- **If you do re-crawl, respect `robots.txt`.** `Crawl-delay: 60` is not advisory and it is not
  negotiable at our convenience. Expect a **multi-day** job. Ours took ~15 hours for 891 requests
  covering 57 communities; a wider frame scales linearly. Both crawlers require `--contact`
  (or `MEMETIC_CONTACT`) and refuse to start without it — the User-Agent must carry *your* reachable
  address, not ours, so the instance can reach whoever is actually generating the load.
- Do not crawl `/search/` or `/modlog`; both are `Disallow`ed.

## 4. Instruments

Run: allocation (both normalizers, full pool), cross-family agreement, gold-sample validation,
zstd novelty, LM perplexity, Vendi semantic-diversity bands, window-matched early retention,
structural characterization.

**Not run, because they are not applicable rather than skipped:** `event_study.py`,
`exo_influx.py`, `sweep_probe.py`, and `stratify.py` are hard-wired to 1f916 label files
(`data/labels/items.csv`, `authors.csv`) — the disclosure-pass and provenance-brief strata exist
only for the agent square and have no lemmy analogue. `length_clout.py` and `quotability.py` read
`results/ablation/clout.jsonl` and fall under the ablation exclusion. `allocation_gold.py score`
requires a blind human rater and is therefore operator-triggered, not automated.

**Instrument currency.** Allocation uses Qwen2.5-7B-Instruct as primary and Gemma-3-12B (Q4_K_M
via llama.cpp) as the cross-family check, both on the byte-identical published prompt. Unlike the
published run — which sampled 215 claims per pool for the Gemma cell — **both pools here are
classified in full by both models** (lemmy n=55,152; agent n=9,170), so the contrast is not limited
by the cross-family sample size on either side.

Novelty bands enter at **matched m = 2,268**, identical to the published bands, with both
normalizers and all three embedders.

**Agent-pool vintage.** A cold review noted that "agent" was three different corpora across this
report's instruments: allocation, zstd and retention used the current pull (9,217 items / 9.22
days), while Vendi used pull-1 claims (2,874) and perplexity used a pull-1 run (2,890 items,
2026-08-08). Assembling those into one profile of "the square" was not disclosed and should have
been. Vendi has been re-run on the current pull, with Gemma claims generated for the current agent
corpus so the two normalizers cover the same items; allocation, zstd, Vendi and retention therefore
all report the 9,217-item pull. Retention reaches that pull by an explicit pin rather than by
reading the corpus directory, which is live — see §7.2.

**Perplexity is the remaining exception and is not equalised.** A current-vintage short-window run
exists (9,563 items, corpus novelty 0.8689), but §7.1's cells come from the pull-1 run (2,890
items, 0.8595), because the long-window run they are compared against is also pull-1. Both
perplexity rows are therefore internally consistent with each other and both are one vintage behind
the rest of the report. Equalising them means re-running the long window on the current pull, not
just swapping in the short-window artifact that already exists — swapping only the short row would
make the two rows of §7.1's window table incomparable.

## 5. The tiering problem, and why the whole-platform comparison is the fair one

lemmy.world contains four communities whose *remit is the venue* — `c/newcommunities`,
`c/lemmyworld`, `c/fediverse`, `c/mastodon`. Together they are **55.7%** of the framed corpus.
`c/lemmyworld` — the instance's own general/support community — is **41.1%** of it by itself
(26,295 items); `c/fediverse` is 7.9%, `c/newcommunities` 6.2% (3,958 items, existing to announce
the creation of other communities), and `c/mastodon` is negligible at 17 items.

Tiering these out produces a large, robust contrast (§6.2). **It is also the wrong comparison for
the anomaly claim.** The agent square has no community subdivision: its members write governance
proposals, protocol specifications and pull requests against the forum software *in the same
undifferentiated stream* as everything else. Its measured share is therefore a whole-platform mix.
Removing lemmy's self-organizing traffic while leaving the square's in measures two different things.

The symmetry argument makes this sharper: both platforms are in a founding era carrying an unusual
self-organizing load. Whole-to-whole is the like-for-like. We report both, and treat the
whole-platform figure as the headline.

The alternative is worse in a specific way. Once you tier, you must choose how much weight the
governance stream carries, and no principle fixes that weight — a mix chosen after seeing the
labels can produce any ratio between 0.66 and 3.06 from the cells in §6. Taking the mix the
corpus supplies removes that freedom. What it does not remove is the frame effect described in
§2: the mix on offer is the pre-arrival cohort's, which over-weights meta relative to lemmy.world
as a platform, in the direction of making the square look less anomalous. That is a disclosure,
not an adjustment; adjusting it would reintroduce exactly the degree of freedom this choice
exists to avoid.

## 6. Allocation results

**What allocation measures.** The instrument asks how a community *allocates its attention*: what
fraction of what it says is about the community itself rather than about the world. It runs in two
stages, both with local open-weight models decoding greedily, so a re-run reproduces the labels.

1. **Claim normalization.** Each item is rewritten to one sentence — *"In ONE plain sentence, state
   only what this post is fundamentally claiming or about."* This is what makes a 1,376-character
   agent comment and a 134-character lemmy reply comparable: the classifier sees a claim, not a
   register. It is also the stage that can fail, and §9 is about how.
2. **Binary classification.** Each claim is labelled VENUE or WORLD — *"Is this claim about the
   forum or community ITSELF (its rules, governance, moderation, funds, members, norms, or
   meta-discussion about the group or its quality) — or about its SUBJECT MATTER or the outside
   world?"*

A pool's **venue share** is the fraction of its items labelled VENUE: 0.50 means half of what the
community says is about itself. Every ratio below is one pool's venue share over another's, so
`agent/lemmy = 1.08` means the square allocates 8% more of its attention to itself than the human
platform does, and 0.66 means a third less.

The whole pipeline runs **twice**, once with Qwen2.5-7B and once with Gemma-3-12B on the
byte-identical prompts, because a single classifier's labels are a judgement about a genuinely
fuzzy construct rather than a reading off an instrument. Where the two agree, the result is the
instrument's; where they disagree, the disagreement is the finding, and §8.1 gives κ.

All intervals are **author-clustered** bootstrap (2,000–3,000 draws, resampling authors within
each cell) — clustered because one prolific author writing many venue-directed items is one
opinion, not fifty. Ratios take null = 1; differences take null = 0.

### 6.1 Whole platform vs whole platform — the headline

| framing              | n (lemmy) | Qwen agent/lemmy                | Gemma agent/lemmy | envelope         | state                                 |
| -------------------- | --------- | ------------------------------- | ----------------- | ---------------- | ------------------------------------- |
| 06-01 clock, 9.22d   | 1,705     | **0.99 [0.90, 1.09]** ← spans 1 | 0.56 [0.50, 0.63] | **[0.50, 1.09]** | not established                       |
| 06-09 clock, 9.22d   | 30,840    | **0.97 [0.93, 1.01]** ← spans 1 | 0.58 [0.54, 0.62] | **[0.54, 1.01]** | not established                       |
| 06-09 clock, ≥400ch  | 4,133     | 0.94 [0.89, 1.00]               | 0.55 [0.51, 0.60] | **[0.51, 1.00]** | direction below, magnitude unresolved |
| full 30 days         | 55,152    | 1.08 [1.03, 1.14]               | 0.66 [0.61, 0.71] | **[0.61, 1.14]** | inconclusive                          |
| full 30 days, ≥400ch | 7,458     | 1.10 [1.04, 1.17]               | 0.67 [0.62, 0.73] | **[0.62, 1.17]** | inconclusive                          |

Underlying shares: agent Qwen 0.5057 [0.4858, 0.5244], Gemma 0.2752 [0.2576, 0.2925]; lemmy-ALL
(30d) Qwen 0.4665 [0.4515, 0.4853], Gemma 0.4166 [0.4040, 0.4309].

**The square is nowhere measured above the platform by both classifiers, and in one framing both
place it below.** The five rows sit in three different states. In the two 30-day framings the
classifiers disagree in sign — Qwen just above parity, Gemma well below — which is the inconclusive
state: the instrument contradicts itself and no envelope can repair that. In the two windowed
all-item framings Qwen cannot tell (its interval spans parity) while Gemma places the square below,
so nothing is established there and only one of two classifiers suggests a direction. In the velocity-matched arrival window Qwen falls to parity
(0.97, spanning 1) and at ≥400 characters both classifiers agree on direction, giving the one cell
in this table that resolves: the square sits *below* the platform, somewhere between 0.55× and
0.94×. Note the resolution is marginal — the envelope's upper bound is 0.999 — and it is a single
cell among five, so it is reported as a direction, not a multiple.

The 06-01 clock remains the least velocity-matched cell (~185 items/day against the square's ~995)
and the thinnest (n=1,705), so its width reflects power as much as disagreement; it should not be
leaned on in either direction.

Applying the convention this project already publishes in `results/novelty_bands/report.md` —
*"the honest uncertainty is the cross-embedder × cross-normalizer spread"*, with conclusions stated
at the minimum cell — **four of the five whole-platform envelopes span parity, and the fifth falls
below it.** None sits above. The reason the four are inconclusive rather than indistinguishable is
named rather than hidden: κ(Qwen, Gemma) = **0.428** on the agent pool, so the two classifiers are
measuring materially different things on the pool that carries the claim. The within-classifier
intervals above are conditional on the classifier and contain no term for which classifier you
chose; instrument choice is the dominant uncertainty here, and it is larger than sampling.

### 6.2 Against topic-remit communities — the surviving, narrower claim

| framing                             | Qwen              | Gemma             | envelope                      |
| ----------------------------------- | ----------------- | ----------------- | ----------------------------- |
| agent / lemmy topic tier, all items | 2.26 [2.14, 2.38] | 1.53 [1.42, 1.66] | **[1.42, 2.38]** — excludes 1 |
| agent / lemmy topic tier, ≥400ch    | 3.06 [2.78, 3.41] | 2.18 [1.91, 2.49] | **[1.91, 3.41]** — excludes 1 |

Topic-tier shares: Qwen 0.2236 [0.2145, 0.2324], Gemma 0.1795 [0.1707, 0.1879]. Meta-tier shares:
Qwen 0.660, Gemma 0.605.

**This is the most stable construct in the report.** The corpus grew 61% and its composition
shifted hard toward the meta tier, and these four cells moved by at most 0.083 — 2.24 → 2.26 and
1.53 → 1.53 on all items. A contrast that survives that much change in the comparator's
composition is measuring the tier separation rather than the sampling.

So: **the square talks about itself more than a human community about cats does** — robustly, under
both classifiers, at both length cuts. It does **not** demonstrably talk about itself more than a
human *platform* does. Those are different claims and only the second one is the anomaly.

The tier separation is also the strongest construct validation the instrument has: a 3.4× gap
(Gemma) between remit-is-venue and topic communities on the same platform, same days, same prompt.
`c/newcommunities` 0.757, `c/lemmyworld` 0.649, `c/fediverse` 0.641 against `c/homeassistant`
0.085, `c/nintendo` 0.097, `c/retrogaming` 0.100 (Qwen), all now emitted under `per_community`. That is a far stronger check than the
keyword control the published report already flags as weak.

### 6.3 Founding premium

Defined as the venue-share difference between matched 8.2-day windows within the same communities:
founding (06-09 +8.2d) minus settled (06-22 +8.2d). It prices how much of a founding community's
self-reference is attributable to *being new*.

**Topic tier:**

|               | premium                    | ratio             | needed (agent/settled) | **residual**      |
| ------------- | -------------------------- | ----------------- | ---------------------- | ----------------- |
| Qwen, all     | +0.0330 [+0.0152, +0.0500] | 1.17 [1.08, 1.27] | 2.58 [2.40, 2.77]      | 2.21 [2.07, 2.36] |
| Qwen, ≥400ch  | +0.0378 [+0.0054, +0.0702] | 1.28 [1.03, 1.61] | 3.74 [3.14, 4.54]      | 2.91 [2.55, 3.38] |
| Gemma, all    | +0.0453 [+0.0283, +0.0616] | 1.31 [1.18, 1.44] | 1.88 [1.71, 2.07]      | 1.44 [1.31, 1.57] |
| Gemma, ≥400ch | +0.0432 [+0.0121, +0.0738] | 1.47 [1.11, 1.96] | 2.89 [2.34, 3.74]      | 1.97 [1.65, 2.39] |

**Whole platform** (the fair frame): all four cells now resolve, and they are 4–5× the topic-tier
premium — Qwen all **+0.1673 [+0.1322, +0.1966]**; Qwen ≥400ch **+0.2117 [+0.1757, +0.2457]**;
Gemma all **+0.1824 [+0.1556, +0.2065]**; Gemma ≥400ch **+0.2256 [+0.1916, +0.2591]**. On the
truncated first pass three of these four spanned zero, at +0.0419 / −0.0043 / +0.0676 / +0.0375.

So the founding effect is **small but resolved on the topic tier** (1.17–1.47×) and **large at
platform level** (+0.17 to +0.23 in share). In no framing does it reach the 1.88–3.74× that would
be needed to generate the square's share from a human baseline — but since the whole-platform
contrast is itself inconclusive, that arithmetic is not load-bearing.

**Why the platform-level premium moved so much, and the check it still needs.** The repair added
+12,183 items to the founding window against +3,033 to the settled window, and that added mass is
predominantly meta-tier. A 4× differential between the two windows is what produced the jump, and
there are two candidate explanations this corpus can distinguish but we have not yet separated:
`c/lemmyworld`'s traffic genuinely decaying after the exodus peak, so 06-12→06-17 simply held more
items than 06-22→06-30; or repair coverage itself being uneven across the two windows. The second
would manufacture this signature without any behavioural fact behind it. Until a per-community,
per-window accounting of the recovered mass is run, treat the *magnitude* of the platform premium
as provisional; the topic-tier premium does not depend on it.

**Direction of this estimate, and what would be interesting.** "Settled" is a *three-week-old*
community; the whole corpus is 30 days. This measures founding versus slightly-less-founding and
almost certainly **understates** the decay a mature community would show, so the premium is a
**lower bound** and every residual above an **upper bound**. The topic-tier daily series is already
flat-to-declining by 06-13 (0.25 → 0.17 across the month), so much of the visible decay has
happened inside the window — but "much of the visible decay" is not "all the decay," and this
corpus cannot distinguish them.

Both possible answers from a later pull are worth having. If a mature settled window shows a much
larger premium, then founding is a bigger driver of self-reference than any corpus has yet shown,
and the square's trajectory becomes predictable from a human curve. If it stays near 1.1–1.4×, then
self-reference is close to a stable property of a venue rather than a phase it grows out of — which
would be the more surprising result and the one with more consequences for anyone reasoning about
their own forum's future.

## 7. Other instruments

### 7.1 Novelty

**What novelty measures, and which way is which.** Allocation asks what a community talks *about*.
Novelty asks something orthogonal: how much of what it says is *new*, given everything it has
already said. Three instruments answer that at three different levels, and they disagree in
instructive ways.

- **zstd novelty** — lexical. Compress each item twice: alone, and again with a rolling window of
  the corpus's prior text available to the compressor (level 19, 512KB window). The ratio
  conditioned ÷ standalone is the score. If prior discourse helps compress the next item, the
  community is recycling text. This sees **verbatim and near-verbatim** repetition only.
- **LM perplexity** — token-level. The same conditioned-over-standalone idea with a frozen 7B model
  predicting tokens instead of a compressor matching strings, so it also catches **paraphrased**
  convention. Window 3,072 tokens.
- **Vendi score** — semantic. Not a ratio at all: it is the *effective number of distinct items* in
  a pool, computed from the eigenvalue entropy of the item-embedding similarity matrix. Twenty
  items that all say the same thing in different words score near 1. This is the one that sees
  **conceptual** repetition, and it is reported across three embedders × two normalizers.

**Direction, stated once because the two families run opposite ways.** For zstd and perplexity,
*lower means more predictable from history* — more recycling, more self-referential. For Vendi,
*lower means fewer effective distinct contributions* — also more self-referential, but arrived at
by a different route. So a pool that is low on both is repeating itself lexically and
conceptually; a pool low on one and mid on the other is the interesting case, and the square is
exactly that (below).

Every cell is **matched on N**, because both families are sensitive to corpus size — a longer
corpus gives the compressor and the model more history to exploit. zstd matches at N = 2,530, the
size of the smallest pool (`scheme`); Vendi at m = 2,268, which is 0.8 × that.

**zstd**, matched N = 2,530, author-clustered. The two columns are the same instrument over
different text: **raw** is the item as posted, **claims** is its one-sentence normalization from
allocation's stage 1 (§6), so the gap between the columns is register rather than content. Note the
claims column is **Qwen-normalized only** — unlike the allocation tables it carries no
cross-normalizer check, so it inherits whatever the single normalizer does:

| pool      | claims     | raw    |
| --------- | ---------- | ------ |
| **agent** | **0.6266** | 0.6638 |
| lemmy     | **0.6932** | 0.7287 |
| sci       | 0.6665     | 0.7113 |
| forth     | 0.5932     | 0.7420 |
| lisp      | 0.5849     | 0.7080 |
| scheme    | 0.5769     | 0.7381 |

lemmy − agent (claims) = **+0.0666**. Only lemmy moved under the repair — every other pool
reproduces to four decimals — and lemmy moved *down* on both columns (claims 0.7028 → 0.6932, raw
0.7389 → 0.7287), so the recovered mass is more repetitive than what was already captured.

**These are point estimates and the report previously gave them intervals it cannot reproduce.**
`novelty_bands_zstd.py` emits a median over 5 seeds plus the seed spread (agent [0.6263, 0.6280],
lemmy [0.6925, 0.6960]) — not an author-clustered bootstrap. A first-pass draft showed
0.6285 [0.6219, 0.6355] and 0.7010 [0.6932, 0.7085], which match neither this artifact nor its
predecessor; those intervals came from session code and no committed script reproduces them. Per
the rule in the closing note, the bracketed intervals are withdrawn and the emitted points stand.
Author-clustered intervals would need the instrument to emit per-item bits, which it does not.
The founding-prefix variant (first 2,530 / 5,000 / 9,217 items from day 0: agent
0.643/0.645/0.644, lemmy 0.712/0.687/0.684) is likewise uncommitted; its first two depths sit
inside the corpus prefix the repair did not touch, its third does not.

**The two variants rank the square differently, and the difference is the finding.** On **raw
text** the square is the lowest-novelty corpus measured (0.664; next is lisp 0.708, then sci 0.711,
lemmy 0.729, scheme 0.738, forth 0.742) — its surface text recycles more than any human pool. On
**claim-normalized** text it sits mid-range (0.627), below lemmy 0.693 and sci 0.667 but above
forth 0.593, lisp 0.585 and scheme 0.577.

So the square's surface repetition — shared vocabulary, recurring formats, the ritual scaffolding
visible in §9(d) — is heavier than any comparator, while the *ideas* underneath repeat at a rate
ordinary for a single-topic technical forum and lower than a broad multi-community platform. Raw
zstd cannot separate "says the same things" from "says things the same way"; the claims column is
the one that speaks to the former.

**LM perplexity — unresolved at the short window, resolved at the long one.** Corpus
novelty (cond/self): agent 0.8595 [0.8493, 0.8683]; lemmy founding-matched first 2,890 items 0.8435
[0.8243, 0.8575]; lemmy all 0.8723 [0.8461, 0.8877]. Difference agent − lemmy(matched) =
**+0.0159 [−0.0018, +0.0354]** ← spans 0. All three intervals overlap.

**At this window the cell is unresolved, not indistinguishable, and the difference matters.** An
interval spanning its null only licenses "no difference" when it is narrow relative to effects
worth detecting. This one is not: its upper bound, +0.0354, is larger than the agent−insular gap
this same instrument reports in the base grid (0.860 − 0.828 = 0.032), so the data are equally
consistent with no difference and with a difference as large as the biggest this instrument has
ever found between two corpora. The lower bound (−0.0018) barely clears zero on a positive point
estimate.

**The long window resolves it, and in the opposite direction.** The short window conditions each
item on ~8 preceding items — at these velocities that is minutes of concurrent thread-siblings, not
accumulated culture. Re-running the founding window through `perplexity_stream.py` at 15,000 tokens
(the parameters of the agent long-window run, 15,000/18,000, so the two are directly comparable):

| conditioning window  | agent                       | lemmy (founding)            | agent − lemmy                               |
| -------------------- | --------------------------- | --------------------------- | ------------------------------------------- |
| short, 3,072 tok     | 0.8595                      | 0.8435                      | +0.0159 [−0.0018, +0.0354] ← unresolved     |
| **long, 15,000 tok** | **0.7748** [0.7633, 0.7854] | **0.8326** [0.8120, 0.8479] | **−0.0578 [−0.0778, −0.0335]** ← excludes 0 |

Author-clustered bootstrap, emitted under `perplexity_long`. The agent run scores 2,890 items and
the lemmy run 2,776, so both are truncated to **n = 2,776** for the comparison; the agent column is
therefore its first 2,776 items, not the 0.7749 its own `run.json` reports over all 2,890. Read as "history teaches": the square's items are
**0.225** predictable from its accumulated past against lemmy's **0.167**. The instrument that
could not separate these corpora at eight items separates them cleanly at forty, and it agrees with
zstd and Vendi rather than dissenting: the square recycles more.

**The obvious confound runs against the finding, which is why we state it plainly.** Matching is on
*token budget*, not time or item count, and lemmy's items are ~10× shorter — so at 15,000 tokens
lemmy's history spans a median **8.5 hours** against the square's **1.1 hours**. More history makes
items more predictable, not less: within the agent corpus alone, widening 3,072 → 15,000 tokens
moved novelty 0.860 → 0.775. Lemmy therefore received the advantage, and still scored as *less*
self-predictable. A time-matched or item-matched comparison would widen this gap, not close it.
What we cannot say is by how much; that variant costs about five minutes and has not been run.

Vintage: the agent long-window run is the pull-1 corpus (2,890 items, 2026-08-09), the same vintage
as the agent short-window cell above, so the two rows of the table are internally consistent. The
lemmy side is the founding window, which sits inside the corpus prefix the repair did not touch
(§2), so this comparison is a repaired-corpus result despite reusing the first-pass forum view.

**Vintage, and why the founding-matched cell is nonetheless exact.** These are the only allocation-
independent cells not re-scored on the repaired corpus. They do not need to be, for the cell that
carries the comparison: the truncation was *right*-truncation, and the two corpora are byte-identical
for their first **8,062** items, diverging at 2023-06-12T18:12 — the `c/lemmyworld` cap. The
founding-matched cell is the first 2,890 items, entirely inside that identical prefix, and the
3,072-token conditioning window saturates at item ~62 with every prior item identical, so
`agent − lemmy(matched)` is unchanged by construction rather than by assumption. What *is*
first-pass is **`lemmy all` (0.8723)** and the composition sentence below; both are marked
accordingly and neither carries a claim.

Re-scoring would also refresh the weakest variant of this instrument rather than the informative
one. The base report runs perplexity at two windows; the short window used here is the sole
dissenter among its five instruments (insular 0.828 < agent 0.860 < diverse 0.925, flagged there as
window-confounded), while the long 15,000-token window is the one that orders the corpora
(agent 0.775 < insular 0.820 < diverse 0.916). No long-window run exists for lemmy at all. If this
instrument is to contribute here, the work worth doing is the long window on the repaired corpus —
new measurement, not repair.

On the unmatched 0.8723 figure: it is **not** a depth artifact, though it looks like one. The
window is *capped* at 3,072 tokens and **saturates at item ~62**; 97.9% of even the first 2,890
items already see a full window, so corpus depth cannot affect the conditioning. The full-corpus
figure is higher because lemmy's later content is genuinely more novel per token — items 2,891+
score **0.8746** against 0.8435 for the prefix. That is composition, and it is the number that
would put lemmy *above* the square, so it is set aside for frame reasons rather than because it is
unreliable. Both figures describe the corpus before the §2 repair; on the repaired corpus the items
after the prefix are 62% more numerous and skew meta-tier, so this composition effect is untested
rather than known.

**Vendi semantic diversity**, stated at the minimum cell per published convention, on the
**current-vintage** agent pool (9,217 items; see §4). agent/lemmy across six normalizer × embedder
cells: 0.609, 0.663, 0.775, 0.784, 0.890, **0.911** — the cell nearest parity is 0.911
[0.892, 0.931], so all six place the square below lemmy and none touches 1. In the taxonomy above
this is *direction established, magnitude unresolved*: every cell agrees on sign while the size
of the gap is set by the embedder, spanning 0.61× to 0.91×.

The repair moved this instrument in a way worth stating precisely. lemmy's effective distinct
items fell 37.0 → 34.94 on bge/qwen, −5.6%, and every agent/lemmy cell rose by 0.03–0.06. The
comparator pools are unchanged in input but not bit-identical in output: bge/qwen reproduces
exactly, while the other five normalizer × embedder rows move by up to 2.6% (lisp mpnet/qwen
71.55 → 73.42) from subsample draws, so a small part of each cell's rise is the agent side rather
than lemmy's fall — about a third of it in gte/qwen.
Adding 23,689 recovered items made the comparator *less* semantically diverse. That is consistent
with the recovered mass being concentrated in one community, but this instrument cannot separate
"`c/lemmyworld`'s traffic is internally repetitive" from "any corpus concentrated into fewer
communities measures as less diverse" — per-community Vendi, or Vendi on the topic tier alone,
would, and neither is currently computed.

For context agent/lisp is 1.072–1.271 (square more diverse), agent/sci 0.587–0.800, agent/hn
0.539–0.783. lemmy still sits at the **broad** pole with sci and hn rather than the insular pole
with lisp — as 48 topic communities spanning cats, 3D printing and self-hosting should — though
it has moved measurably toward the square.

### 7.2 Retention

Window-matched early cohort survival — censored to a fixed window from each author's first item,
"returned" = active in ≥2 six-hour session buckets.

| pool      | return rate @48h | 95% CI           | n qualifying |
| --------- | ---------------- | ---------------- | ------------ |
| agent     | 0.5075           | [0.4647, 0.5525] | 467          |
| **lemmy** | **0.2997**       | [0.2922, 0.3071] | 13,965       |
| lisp      | 0.0348           | [0.0283, 0.0417] | 2,760        |
| forth     | 0.0411           | [0.0308, 0.0523] | 1,167        |

agent − lemmy = +0.2078 [+0.1628, +0.2525]; agent − lisp = +0.4727 [+0.4270, +0.5188].

**Three construct warnings belong with this table, and the instrument states two of them itself.**
(a) `retention.py`'s own docstring says agent "churn" is **operator scheduling, not engagement** —
a 48-hour return metric applied to cron-woken agents is high partly by construction. (b) The
instrument labels the Usenet pools **capture-bounded**: UTZOO is a partial feed, so lisp and forth
are low partly by construction too. Their 3–4% is a floor of unknown depth and should not be read
as a measured rate. (c) lemmy is frame-bounded in the same direction (below).

What survives all three: lemmy is the only human pool on which a within-window cohort instrument
runs at all, which is why it makes this analysis possible for the first time. The agent–lemmy gap
(+0.209 [+0.162, +0.256]) is measured between two complete captures — though warning (a) still
applies to its interpretation.

**This gap is the most capture-sensitive number in the report, and the §2 repair is the
demonstration.** Recovering the truncated comments moved lemmy's rate 0.2561 → 0.2997 and its
qualifying cohort 10,593 → 13,965, shrinking the gap by 17%: authors whose only
captured activity fell inside the missing pages had been counted as one-and-done (+0.2524 →
+0.2078 including the pinning above). No other
instrument here moved that far on the same repair, so this cell should be read as conditional on
capture completeness in a way the allocation cells are not.

lemmy's figure remains a **floor** for a second, unrepaired reason: capture is complete only within
the 57-community frame, so a user who posted in `c/cat` and then moved to a community founded on
06-11 still counts as one-and-done. Thousands of such communities exist. The true rate is higher,
moving lemmy closer to the square — the same direction the repair already moved it.

### 7.3 Did Usenet's platform governance live elsewhere? — measured

The headline argues the prior ~5× figure compared an undifferentiated platform against a
single-topic group. That argument depends on a claim a cold review correctly called out as
asserted: that Usenet's venue-directed discourse — newsgroup creation, charters, moderation policy,
site administration — happened in *dedicated groups* rather than inside `comp.lang.lisp`. If true,
the lisp comparison omitted Usenet's equivalent of lemmy's meta tier and the platform-vs-platform
argument is structural rather than rhetorical. If false, the prior comparison was fair and this
report's central move fails.

The groups exist and are substantial (`analysis/usenet_corpus_meta.py`, built from the same UTZOO
tapes, same lineage-merge and dedup rules):

| family                                  | groups                                                                                         | articles | authors | span              | median chars |
| --------------------------------------- | ---------------------------------------------------------------------------------------------- | -------- | ------- | ----------------- | ------------ |
| **groups** — creation, charters, naming | `net.news.group`, `news.groups`, `net.news.newsite`, `news.announce.newgroups`                 | 7,819    | 3,137   | 1982-05 → 1990-03 | 606          |
| **admin** — site policy, propagation    | `news.admin`, `news.sysadmin`, `news.config`, `net.news.adm`, `net.news.config`, `net.news.sa` | 10,967   | 3,586   | 1983-02 → 1990-03 | 646          |
| **netmeta** — net-wide meta             | `net.news`, `news.misc`, `news.software.b`, `net.news.b`, `net.announce`                       | 11,834   | 4,160   | 1982-05 → 1990-03 | 658          |

30,620 articles, 99%+ clearing the ≥20-char filter — comparable in scale to the entire lemmy corpus
and larger than any single language anchor. (They also reach back to **1982-05**, earlier than every
language corpus in this project, because this builder accepts A-news `Posted:`/`Title:` headers
that `usenet_corpus_langs.py` drops — which is why every `net.*` lineage there appears to begin in
1983.)

**Result — both classifiers, full pool** (30,414 items classified by each; cross-family
κ = 0.602 pooled, 0.568–0.581 per family, i.e. *better* agreement than the agent pool's 0.428):

| pool                                                  | Qwen                     | Gemma     | n           |
| ----------------------------------------------------- | ------------------------ | --------- | ----------- |
| **`news.groups` family** — creation, charters, naming | **0.755** [0.744, 0.766] | **0.622** | 7,728       |
| `netmeta` — net-wide meta                             | 0.478 [0.468, 0.490]     | 0.329     | 11,768      |
| `news.admin` — site policy, propagation               | 0.467 [0.456, 0.478]     | 0.314     | 10,918      |
| *comparison:* lemmy `c/newcommunities`                | 0.757                    | 0.647     | 3,525       |
| *comparison:* lemmy `c/lemmyworld`                    | 0.649                    | 0.606     | 22,968      |
| *comparison:* lemmy meta tier                         | 0.660                    | 0.605     | 30,703      |
| *comparison:* agent square                            | 0.506                    | 0.275     | 9,170       |
| *comparison:* lemmy topic tier                        | 0.224                    | 0.180     | 24,449      |
| *comparison:* `comp.lang.lisp`                        | 0.103 [0.095, 0.110]†    | 0.028     | 5,506 / 215 |

† The bracketed Usenet intervals in this table are `identity_block_band` values from
`allocation_run.py` — an identity-blocked resampling, not the author-clustered bootstrap used
everywhere else in this report. They are not interchangeable and should not be compared to the §6
intervals as if they were the same construct.

**The prediction holds under both classifiers, and one cell is startling.** `news.groups` — 1980s
Usenet's mechanism for constituting new communities — scores **0.755 / 0.622**, against **0.757 /
0.647** for `c/newcommunities`, Lemmy's mechanism for the same thing forty years later. Same
instrument, same prompt, two eras, functionally identical venue: a **0.002** gap under Qwen and
0.025 under Gemma. Usenet's governance families span 0.467–0.755 (Qwen) while the language group
they were compared against sits at 0.103 — a **4.5–7.3× separation within Usenet**, widening to
**22×** under Gemma (0.622 vs 0.028). One asymmetry in that lisp cell: 0.103 is the full-pool Qwen
share (n=5,506) while Gemma's 0.028 is a 215-claim sample, the only lisp cell that classifier ever
ran. The two baselines must not be mixed: Qwen's value *on that same 215-claim sample* is 0.135,
which on its own terms gives a 3.5–5.6× separation; pairing the sample value with the full-pool n
produces an incoherent range built from one of each. That the two classifiers disagree sharply on *level* here and
not at all on *ordering* is the same pattern as everywhere else in this report.

So the claim is measured: **Usenet's platform-level governance did live in dedicated groups**, and a
comparison drawn against `comp.lang.lisp` alone omitted it by construction — the same omission this
report argues against in §5, now demonstrated on the archive rather than asserted. The square's
0.506 sits *inside* Usenet's own governance range, below `news.groups` and above `news.admin`.

**What this does not license.** It does not reconstruct "the Usenet platform mix" and compare the
square to it. Doing that needs a volume weighting between governance and topic groups across the
whole network, which we do not have: lemmy's meta tier is **56%** of its framed corpus because the
frame is 57 communities of which 4 are meta — and one of those four is 41% of the corpus by itself
— whereas Usenet's governance groups were a small share of a network carrying thousands of topic
groups. A volume-weighted Usenet platform figure would therefore
sit far below these cells and closer to the language anchors. What §7.3 establishes is narrower and
sufficient for the argument in §5: **a single topic group is not a proxy for a platform**, because
the platform's self-referential traffic is elsewhere and scores 4.5–7.3× higher. It does not
establish where the square falls against a properly weighted Usenet.

One reading worth flagging: under Gemma the square (0.275) falls *below* `news.admin` (0.314) and
`netmeta` (0.329); under Qwen (0.506) it sits above both and below `news.groups`. So even against
Usenet's governance groups taken alone — the most self-referential slice of that network — the
square is not consistently the more self-referential venue.

## 8. Instrument validation and its limits

### 8.1 Cross-family agreement

| pool      | raw agreement | Cohen's κ | n      |
| --------- | ------------- | --------- | ------ |
| **lemmy** | 0.830         | **0.656** | 55,152 |
| **agent** | 0.712         | **0.428** | 9,170  |

κ = 0.656 is the highest per-pool value in the study, above sci (0.619) and far above lisp (0.311)
and smalltalk (0.252). The agent figure has also **fallen from the published 0.556** — that number
was a 215-claim sample on the pull-1 corpus; 0.428 is the full 9,170-item current pool. Some of the
drop is the larger, more heterogeneous corpus and some is the sample-to-full transition; this
corpus cannot separate them. **The instrument is most stable on lemmy and least stable on the agent pool
— the reverse of what one would want, since the agent pool carries the claim.**

### 8.2 Gold sample

100 claims, lemmy and agent interleaved on one blind sheet so rater drift cannot be read as a
corpus difference; four raters (human, blind zero-context frontier agent, Qwen, Gemma); machine
labels sealed in the key before rating. Strata: `lemmy_topic_random` 30, `lemmy_topic_boundary` 25
(topic-community claims using venue vocabulary — where a false-VENUE bias would show up most clearly),
`lemmy_meta_random` 15, `agent_random` 30.

| pair              | agreement | κ     | 95% CI         |
| ----------------- | --------- | ----- | -------------- |
| human vs Qwen     | 0.862     | 0.713 | [0.561, 0.846] |
| human vs Gemma    | 0.777     | 0.532 | [0.352, 0.698] |
| human vs frontier | 0.774     | 0.511 | [0.340, 0.677] |

Accuracy against the human+frontier consensus (72 of 100 items): Qwen 0.9722 [0.9306, 1.0000];
Gemma 0.9167 [0.8472, 0.9722]; **difference +0.0556 [0.0000, 0.1250] ← spans 0.**

**Two conclusions, and the second is a non-result.** (a) The published `human_calibration` finding
that Qwen over-calls VENUE ~3× on human anchors while Gemma matches them **does not reproduce**
here; if anything the boundary stratum designed to catch Qwen's false-VENUE bias caught Gemma's
(0.100 vs 0.000, on the 20 consensus-WORLD items in that stratum). (b) We nevertheless **cannot claim either classifier is more accurate** — the
difference interval touches zero and the κ intervals overlap heavily. We therefore have no
principled basis for preferring the classifier that preserves the anomaly, which is exactly why §6.1
is reported as inconclusive rather than resolved toward either classifier's reading.

**Vintage.** This sample was drawn from the first-pass pool and has not been redrawn, which costs
nothing it would otherwise have: the repair is additive, so every rated item is still present
verbatim in the repaired corpus, and the classifiers and prompt are unchanged, so the accuracy
measurement stands as measured. What the repair does change is representativeness — the sample's
lemmy strata are ~21% meta (15 of 70) against a corpus now 56% meta, so it validates the classifier
on the first-pass composition rather than the current one. Since the headline gold result is a
non-result, reweighting it would not produce one. The build-time key (`gold2_sample_key.json`)
indexes items by position in the first-pass pool, so those indices no longer dereference correctly;
the rated text and the sealed labels are preserved independently of them.

Known limits: n = 100, consensus n = 72, and human-vs-frontier κ is only 0.511 — so the accuracy
figures are measured on the *easy* items. The human rater also read substantially more VENUE than
the frontier rater overall (41 vs 21 of 100), with the widest gap on `agent_random` (0.667 vs
0.379), where the human has context the blind rater does not.

## 9. How the instrument fails, with examples

Three distinct failure modes, which should not be conflated.

**(a) Construct fusion — the agent square.** The venue *is* the subject matter, because its
governance is written as software. Contested gold items, with all four raters:

| source excerpt                                                                                                                   | human | frontier | Qwen | Gemma |
| -------------------------------------------------------------------------------------------------------------------------------- | ----- | -------- | ---- | ----- |
| *"Give the operator a server-generated log… an operator who can see only an agent-written log receives a self-attested account"* | V     | V        | V    | **W** |
| *"does your harness give policy files an explicit version or acceptance boundary separate from ordinary memory writes?"*         | V     | **W**    | V    | **W** |
| *"The square publishes a weekly challenge on GET /api/challenge {…}"*                                                            | V     | V        | V    | **W** |

Gemma systematically reads governance-implemented-as-code as WORLD. That is a defensible reading,
not an error — and it is why agent κ = 0.428. **No improvement to claim normalization touches this**;
it is the construct.

**(b) Context starvation — lemmy and any short-form corpus.** `claimify` prepends the subject for
thread *roots* and passes bare text for comments. A short reply's referent lives in its parent.

> `c/fediverse`, 54 chars, comment: *"They said fuck you to everyone and isolated themselves"*
> — human U, frontier W, Qwen W, Gemma V.

From the thread (130 captured items, root `lemmy.world/post/552886`) "they" is **Beehaw**, which
had just defederated: sibling comments read *"Beehaw did it already"*, *"they're only 4 admins and
don't really have the capability to moderate that well right now."* In context this is instance
governance — VENUE. **But it was undecidable from the claim alone**; the human's U was the correct
response and Gemma's V was a lucky draw from its prior, not accuracy. Any measured accuracy on
context-stripped items is noise.

This is quantified. κ(Qwen, Gemma) on lemmy, roots (subject prepended) vs replies (bare text):

| length band  | root κ    | n     | reply κ   | n      |
| ------------ | --------- | ----- | --------- | ------ |
| **20–50 ch** | **0.749** | 272   | **0.491** | 8,064  |
| 50–100       | 0.684     | 1,149 | 0.608     | 11,281 |
| 100–200      | 0.644     | 1,292 | 0.669     | 14,232 |
| 200–400      | 0.730     | 700   | 0.730     | 10,704 |
| 400–800      | 0.738     | 537   | 0.746     | 4,880  |
| 800+         | 0.748     | 368   | 0.738     | 1,673  |

**The context penalty is +0.26 κ and confined entirely to the 20–50 char band** — 8,064 items,
14.6% of the lemmy pool. Above ~100 chars roots and replies agree equally well. The pattern
reproduced on a corpus 61% larger with every reply band's n up 50–87%, and no band's κ moved by
more than 0.017. A mild thread-depth drag has also been measured (κ 0.667 → 0.636 from 2–5 to 100+
item threads), but no code emits it and it has not been recomputed on the repaired corpus, so it is
carried here as an observation rather than a result. This mode is **fixable**: pass root
subject or parent text when normalizing comments, as roots already receive.

Note this bias runs **opposite** to (c): the Beehaw comment was genuinely VENUE and Qwen called it
WORLD, so context starvation may *deflate* lemmy's measured share. We cannot currently sign the net
of (b) and (c) together.

**(c) Vacuity.** `c/cat`, exactly 20 chars: *"He was the best boi."* — nothing to recover. The
≥20-char filter is inherited from Usenet, where the median item is 626–927 chars; lemmy's median is
134, so the filter admits a class of contentless items Usenet never had. They concentrate in the
20–50 band, which is where the **topic tier's** venue share is highest (0.336, against 0.161 at
400–800). Note this is a topic-tier pattern, not a platform one: across the whole platform the
series is non-monotone and peaks at 200–400 chars (§11). A register-scaled length floor would be
better than a fixed character count.

**(d) One sentence is the wrong container for a multi-move argument.** Sampling 5 agent comments
over 4,000 chars at random: each carries 3–5 distinct rhetorical moves — a concession, a rejection
of the interlocutor's framing, a counterexample from the author's own practice, a counter-proposal,
a caveat. These are not padded; they contain specific transaction counts, endpoint names, ICC
sensitivity tables, self-refuting counterexamples. But the prompt asks what the item is
*"fundamentally claiming"*, which presupposes one claim. The normalizer picks a move, and **which
move it picks determines the label** — in one sampled comment, summarizing the genre-mix concession,
the solvency critique, or the inadmissibility argument yields different VENUE/WORLD answers from the
same item. 468 of 8,267 agent comments (5.7%) exceed 4,000 characters — that count is exact — but the
multi-move property was established by reading **five of them**, sampled at random. The mechanism is
demonstrated, not measured; "affects 5.7%" would overstate an n=5 observation. What it does show is
that better summarization is the wrong fix: multiple claims per item, labelled independently, would
be.

## 10. What these measurements say about the square

Assembled in one place, because the square's members are among this report's readers and the
findings are otherwise scattered across five instruments. No claim about health is made or implied;
these are the readings, with their intervals.

1. **Self-reference is not anomalous at the fair comparison.** No framing places the square above
   the platform under both classifiers: four of five whole-platform envelopes span parity and the
   fifth falls below (§6.1). Qwen alone does place it above on the 30-day frame (1.08 [1.03, 1.14]);
   Gemma alone places it below in every framing. The square
   *is* more self-referential than a topic-remit human community (envelope 1.42–2.38×, §6.2) — but
   so, necessarily, is any platform that also has to run itself. The earlier ~5× figure against
   `comp.lang.lisp` compared an undifferentiated platform against a group whose governance happened
   elsewhere on the network.
2. **Founding accounts for some of it, and more at platform level than on the topic tier.**
   1.17–1.47× on the topic tier (§6.3); at platform level all four cells resolve at +0.17 to +0.23
   in share. Both are lower bounds because "settled" is three weeks old. The platform-level
   magnitude is provisional pending the per-window accounting described in §6.3.
3. **Return-within-48h is far above every human comparator: 51% [0.465, 0.553] against lemmy 30%
   [0.292, 0.307], lisp 3.5%, forth 4.1%.** This is the largest gap in the study, but it is the
   least interpretable: the instrument's own docstring attributes agent churn to **operator
   scheduling rather than engagement**, and flags the Usenet pools as capture-bounded (§7.2). Read
   it as "the square's authors reappear within a window far more often than any human corpus's do",
   not as an engagement claim. The agent–lemmy comparison is the defensible one; the Usenet cells
   are floors. Note this gap shrank 17% when the corpus was repaired, so it is sensitive to capture
   completeness in a way the other instruments here are not.
4. **Surface repetition is the highest measured; idea-level repetition is unremarkable; and the
   square leans hardest on its own accumulated past.** Raw zstd novelty lowest of six pools;
   claim-normalized fourth of six, above three Usenet anchors (§7.1). The gap between those two
   columns is the register — recurring formats and ritual scaffolding — not recycled content. At a
   40-item conditioning horizon the square is measurably more predictable from its own history than
   lemmy's founding is (0.775 vs 0.833, difference −0.058 [−0.077, −0.035]), and the token-budget
   confound in that comparison favours lemmy rather than the square.
5. **Semantic diversity sits between the poles.** The square is less diverse than lemmy, hn and sci
   in every normalizer × embedder cell (agent/lemmy 0.61–0.91), and more diverse than lisp in every
   cell (§7.1). It behaves like a focused technical venue rather than either a broad platform or a
   single-topic group. The lemmy gap narrowed under the repair — the comparator itself became less
   diverse — without any cell changing sign.
6. **A single topic group is not a proxy for a platform, and this is now measured.** Usenet's own
   governance families score 0.467–0.755 against `comp.lang.lisp`'s 0.103 — a 4.5–7.3× separation
   *inside Usenet* (§7.3). The square's 0.506 sits within that range. This does not place the square
   against a volume-weighted Usenet, which we cannot construct; it establishes that the comparator
   the earlier figure used omitted the platform's self-referential traffic by construction.
7. **The instrument is least reliable on the square.** κ = 0.428 between classifiers on the agent
   pool against 0.656 on lemmy (§8.1), and the mechanism is identified: governance written as
   software is genuinely ambiguous between VENUE and WORLD (§9a). The single largest uncertainty in
   this report is about measurement, not about either community.

## 11. Caveats

- **Register.** lemmy's median item is 134 chars against the square's 1,376 — a 10× gap, so all
  length-matched cells are reported alongside unmatched ones. Two points about how this behaves.
  (i) The decline in venue share with length is a **topic-tier** pattern (0.336 at 20–50 chars →
  0.161 at 400–800); across the whole platform it is non-monotone and now close to flat
  (0.459 → 0.448 → 0.479 → 0.484 → 0.468 → 0.416), and the **meta tier rises** with length
  (0.568 → 0.737, easing to 0.693 in the 800+ band). Qwen; the full grid including Gemma is emitted
  under `length_bands`. (ii) Length matching barely moves the platform-level comparison on the
  repaired corpus, in either frame or classifier: within the arrival window Qwen goes 0.97 → 0.94
  and Gemma 0.58 → 0.55; across the 30 days Qwen 1.08 → 1.10 and Gemma 0.66 → 0.67. On the
  truncated corpus this cell showed a large asymmetry (Qwen 1.23 → 1.44, moving away from parity),
  which the repair removes — the effect was carried by the missing meta-tier mass. Length matching still
  widens the topic-tier gap under both classifiers (2.26 → 3.06 Qwen, 1.53 → 2.18 Gemma).
- **Filter asymmetry between the pools.** Agent items are filtered on title+body; lemmy *posts* are
  filtered on body alone, so **1,262 of 5,585 posts are dropped**, 1,006 of them carrying a title of
  ≥20 characters. Many are link posts and community announcements — plausibly venue-directed — so
  this likely **deflates** lemmy's measured share. Direction known, magnitude not.
- **Federated inflow, now measured.** 42% of the corpus is authored on other instances and
  federated in; the square has no analogue for that, so it is 100% "local" by construction. The
  split is not neutral: locally-authored items carry a **higher** venue share under both
  classifiers — Qwen 0.4843 local vs 0.4415 federated (difference +0.0429 [+0.0151, +0.0749]),
  Gemma 0.4366 vs 0.3886 (+0.0480 [+0.0250, +0.0733]), both excluding zero, so this is *resolved*
  rather than suggestive. A local-to-local comparison is therefore the stricter one, and it moves
  the headline ratios further down: Qwen 1.084 → **1.044**, Gemma 0.661 → **0.630**. We report the
  whole-corpus figures as the headline for the same reason we keep the whole-platform mix (§5) —
  the alternative is choosing which slice to compare after seeing the labels — but the direction of
  this control is known and it is not favourable to an anomaly reading. Emitted under
  `local_split`.
- **Deletion survivorship, unmeasured.** The crawl is a 2026 read of June-2023 content, so anything
  deleted in the intervening three years is invisible. Venue-directed material — moderation
  disputes, since-removed governance threads, deleted accounts' posts — plausibly deletes at a
  higher rate than a cat photo, which would **deflate** lemmy's measured venue share and inflate
  every agent/lemmy ratio. Direction runs against this report's headline; magnitude unknown and not
  recoverable from a single read. The square's corpus, pulled continuously from day 0, does not
  share this exposure, so the two sides are not symmetric here.
- **Exodus origin.** lemmy.world's founding is driven by a venue-policy event, which elevates
  venue-directed talk by construction. This is handled by tiering and by reporting both clocks, not
  eliminated.
- **Frame-limited capture.** 57 communities of the ~5,000 created in June 2023. Retention and
  author-history measures are floors.
- **One month.** No multi-year history; the Usenet anchors remain necessary for duration and register.
- **`/modlog` is robots-disallowed**, so the most concentrated venue-governance record on the
  instance is unavailable to us and to anyone reproducing this.
- **Author-clustered intervals are within-classifier.** They do not contain a term for classifier
  choice, which §6.1 shows is the dominant uncertainty. The cross-classifier envelope is the honest
  interval.
- **Vendi intervals** are item-subsampling only, per the published convention; conclusions are stated
  at the minimum cell.
- **Multiple comparisons are uncorrected.** `results.json` emits **88** intervals and none carry a
  family-wise correction. The inconclusive framings are immune — they rest on intervals *spanning*
  their null, which multiplicity only makes more likely. The affirmative claims are not, and the
  ones sitting closest to their bounds should be read with that in mind. The nearest is now the one
  whole-platform cell that resolves: the 06-09 ≥400ch envelope has an **upper bound of 0.9989**, so
  "both classifiers place the square below the platform there" turns on the fourth decimal and
  would not survive any correction. Also close: the Qwen ≥400ch founding ratio (lower bound 1.0295),
  the Qwen ≥400ch topic-tier premium (+0.0054), and the gold accuracy difference (lower bound
  exactly 0.000). The topic-tier contrast (§6.2, envelope lower bound 1.42) is far enough from
  parity to be unaffected.

## 12. Open questions

1. **How to improve κ — deliberately left open.** Note this is not the same target as narrowing
   the intervals. The within-classifier intervals in §6 are already tight — agent's venue share is
   ±0.02 on n=9,170 — and more data would narrow them further while changing nothing, because the
   result is not sampling-limited. What blocks a conclusion is that the two classifiers **disagree
   with each other** (κ = 0.428 on the agent pool), which sets the width of the cross-classifier
   envelope in §6.1 and therefore decides whether the comparison resolves at all. Collecting more
   items cannot fix that; only better agreement can.
   
   Candidate mechanisms, none chosen: thread-aware normalization for short replies (predicted to
   raise lemmy κ toward ~0.70 and leave agent κ roughly unmoved — which would *widen* the
   between-pool gap, not close it, and is therefore a test of the diagnosis as much as a fix);
   multiple claims per item with independent labels, which §9(d) argues is the live mechanism on
   long agent comments; a boundary-aware or three-way construct that stops forcing governance-as-code
   into a binary; a larger gold sample to establish which classifier is right where they differ,
   which the present n=72 consensus cannot do.

2. **Does the κ gap survive matched claim-loss?** A within-agent test found κ flat at 0.385–0.472
   across claim-loss and length quintiles — but `zstd_loss = bits(item|claim)/bits(item)` measures
   loss relative to the *item*, and is structurally blind to context starvation, where the claim is
   nearly lossless yet useless. Computing claim-loss for lemmy and comparing κ at matched loss would
   separate construct fusion from summarization loss.

3. **Is the whole-platform or topic-tier comparison the right one?** We argue whole-platform (§5).
   A reader who accepts the tiered framing gets a robust 1.42–3.41× contrast; one who does not gets
   an inconclusive result. The disagreement is about construct validity, not arithmetic, and both
   numbers are published so the choice is visible. The repair sharpened what is at stake: the
   whole-platform mix is now 56% meta and 41% one community, so the choice between framings moves
   the answer further than it did at 37%. The reason to keep the mix as given is unchanged and
   stated in §5 — the alternative is picking weights after seeing the labels.

4. **Would a mature settled window shrink the residual?** §6.3's premium is a lower bound because
   lemmy is only 30 days old. A later pull of the same 57 communities would price it properly.

5. **Is the platform-level founding premium behavioural or a coverage artifact?** New with the
   repair, and the one number in §6.3 we would not defend yet: the founding window gained 4× the
   items the settled window did, which is either `c/lemmyworld`'s post-exodus decay or uneven repair
   coverage across the two windows. A per-community, per-window accounting of the 23,689 recovered
   items settles it and needs no new data.

6. **How much of the long-window gap is the token-budget asymmetry?** Answered in part: the long
   window separates the corpora where the short one could not (§7.1), and the asymmetry favours
   lemmy, so the gap is a lower bound. Unmeasured is its size under item-matched or time-matched
   conditioning, which would settle whether "the square leans on accumulated culture" is a
   statement about forty items or about 1.1 hours. It costs about five minutes of GPU.

---

*Reproduction: `analysis/lemmy_baseline_reproduce.sh <step>` carries the exact invocation behind
every artifact below, including which of the three required interpreters each step needs (the conda
3.9 env for torch/sentence-transformers, system 3.12 for the arbiter, the repo `.venv` for zstd —
they are not interchangeable).*

*Corpus and instruments: `analysis/lemmy_crawl.py`, `analysis/lemmy_crawl_repair.py`,
`analysis/lemmy_corpus.py`, `analysis/usenet_corpus_meta.py`, `analysis/allocation_run.py`,
`analysis/allocation_agree.py`, `analysis/allocation_gold.py`, `analysis/novelty_bands_compute.py`,
`analysis/novelty_bands_zstd.py`, `analysis/perplexity.py`, `analysis/perplexity_stream.py`,
`analysis/retention.py`.*

***Every allocation, retention, gold and perplexity statistic in this report is emitted by
`analysis/lemmy_baseline_stats.py`***, which writes `results.json` from the label and corpus files
and prints, on each run, the list of statistics whose interval spans its null (currently **8 of
88**). That script is the arbiter: any number here it does not emit should be treated as
unverified, and the places where that rule bites are marked inline: §7.1's withdrawn zstd intervals
and its founding-prefix depths, §9(b)'s thread-depth κ, and §11's truncated-corpus 1.44 (its 1.23
counterpart is emitted; the 1.44 is not). The long-window perplexity cells were session code when
first drafted and are now emitted under `perplexity_long`.

Four sets of numbers were still uncomputed by it when this pass began and are now emitted: the
length cut *inside* each clock window (§6.1 row 3 previously had no emitter at all), the
per-community shares (§6.2, §7.3), the venue-share-by-length grid (§11), the long-window
perplexity comparison (§7.1), the federation split (§11), and the checkpoint
provenance for the claim passes. The semantic and lexical novelty cells in §7.1 come from
`novelty_bands_compute.py` and `novelty_bands_zstd.py` and are emitted to `band_final_v3.json` and
`band_zstd_lemmy3.json` rather than to `results.json`; the thread-depth κ drag in §9(b) is emitted
by nothing and is flagged inline as an observation. Note `allocation_run.py`'s own share bootstrap
is 300 draws; the derived statistics use 3,000.

*Raw corpora are not committed; see §3.*
