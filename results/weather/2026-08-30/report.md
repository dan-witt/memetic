# 1f916 weather · 2026-08-30 (issue #17)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-31 08:19 UTC (last in-scope item 08-30 23:59:48), hard
cutoff **2026-08-31 00:00 UTC**. In scope: **35,653 items** (≥ 20 chars, moderation placeholders
excluded), 1,365 authors, Aug 5 → Aug 30, complete, 8.32 hours of margin. Issue window: **2,062
items across one calendar day**, 08-30. **The idea series moved, by the largest single-issue fall
it has ever taken.** The window-level median — the cell promoted at issue #15 — fell **0.0056** to
**0.1272**, second-lowest on record and **0.2% above the forth anchor at 0.1269**. The sub-forth
rate went with it to 46.2%, and the demotion earns its keep: holding the level fixed, that rate
would read **7.7%**, so the rate is the level's shadow and not a second finding. Everything else
this issue is quiet — arrivals 11, moderation flat, no published day moved, the shared-prefix
assertion back and holding at 0 of 837. **Issue #8's decider fires a tenth consecutive time and is
the deepest yet at 5.91 counting SE, and this issue stops leading on it.** The axis it is built on
was measured this week and carries about eight points; the level's sign against the human
comparator inverts under symmetric measurement. The rule is reported as what the rule says. It is
not reported as a finding about the square.*

![Four panels: idea diversity dropping onto the forth anchor on the newest windows; author inflow at 11, a sixth consecutive fall; register up to 0.6621, tied with 08-26; daily venue share at 0.4214, a tenth day-endpoint with the trailing mean below the lemmy.world platform bound.](figure.png)

## The idea level fell onto the anchor

The published cell is the window-level median on one basis, so every issue's windows are
recomputed from this issue's series and the column is one currency throughout:

| one-basis median | #12 | #13 | #14 | #15 | #16 | **#17** |
|---|---|---|---|---|---|---|
| | 0.1340 | 0.1324 | 0.1302 | 0.1293 | 0.1328 | **0.1272** |

The **−0.0056** step is the largest fall of the sixteen issue-to-issue moves the series has; the
next largest is −0.0038 at issue #3. It is the second-largest move in either direction — issue #6
rose +0.0071 — so this is a record fall, not a record move. The level is the second-lowest recorded,
above only issue #5's 0.1265, and it sits **0.2% above forth** — for practical purposes, on the
anchor. The issue's 50 added windows have a mean of 0.1292 alongside that median. (Two constructions sit
close together below: the one-basis median moves −0.0056, and the threshold decomposition's
added-window split moves −0.0053. They are different partitions of the same series, not a
discrepancy.)

**The sub-forth rate is the same fact told through a threshold.** It reads 46.2% (24 of 52) against
issue #16's 19.2%, and Fisher on the nominal counts gives p = 0.0061 — the first time that test has
returned anything since the cell was demoted. It licenses nothing extra.
`weather_dip_rate.py --threshold` decomposes it: with the median shift of −0.0053 removed, the rate
would be **7.7%**. The whole move is level. Nineteen of the 24 sub-forth windows are within 0.005
of the anchor, which is what a distribution sitting on a threshold looks like. This is exactly the
case issue #14 built the demotion for and issue #15 acted on, arriving one issue later.

What the level does **not** support: a trend. The four moves before it are the oscillation the column
has always shown (−0.0016, −0.0022, −0.0009, +0.0035), and a single step, however large, is one
point. Rolling halves read 0.1324 → 0.1310, an accumulation statistic reported and not read. At
0.1272 the issue's windows remain inside the forth-to-sci corridor, at its floor.

## The decider, and why this issue stops leading on it

The trailing five-day mean at the 08-30 endpoint is **0.4235** (0.4245 at 08-29), against the
0.4515 bound. Depth **0.0280** on a counting standard error of **0.00474** is **5.91 SE**, the
deepest the run has been, and the mean has now been below the bound at **ten consecutive
day-endpoints** (08-21…08-30) — one run sharing four of five days at each step, not ten readings.
Recomputed over incumbents only the same five days give **0.4226**, below the published figure for
a fourth consecutive issue, so the level does not come from the arrivals. Issue #16's bar required
08-30 below 0.5615; it read **0.4214** and cleared it by 0.140.

Every number above is unchanged in construction and correct. What has changed is what the series is
willing to conclude from it.

**The axis carries about eight points.** [`results/venue_conflation`](../../venue_conflation/README.md),
committed this week, scores 2,160 items from each venue under one predicate with three outcomes and
no default clause:

| | venue | external | none | of-subject venue |
|---|---|---|---|---|
| 1f916 | **0.693** | 0.246 | 0.060 | 0.738 |
| lemmy.world | **0.417** | 0.368 | 0.215 | 0.531 |

Three consequences for this cell, in order of how much they bite.

1. **The level's sign against the comparator inverts.** Published, the square sits 0.042 *below*
   lemmy's 0.4665. Measured symmetrically it sits **0.277 above**. So "the square attends to
   itself less than a human platform founding did" is not supportable, and this issue does not say
   it.
2. **The comparator is not partitioning the same thing.** lemmy carries 3.6× the subjectless
   content — 21.5% against 6.0%. A binary classifier must assign all of that somewhere, silently,
   and differently for each venue. No offset repairs that.
3. **The discrimination is eight points.** On subject-bearing items the split separates 96.4% from
   88.2%; independent audits on runnable posts (99.1 vs 92.0) and a two-way item sample (92.9 vs
   85.5) agree. It is a real signal and a weak one.

**What survives untouched is the trend**, which is what the standing caveat has always said is the
clean object. Venue share falls under every scoring tried this week, and the direction is the one
thing every predicate agreed on. The exact slope is carried in no artifact, so no rho is quoted
here; what `results/venue_conflation` supports is the sign, not a coefficient.

**And this is not evidence of collapse.** A subject axis cannot separate a community recycling its
own text from one whose surface is expanding into checkable reality. The square minted a token on
Base, publishes a witness file with a cron backstop, signs with ed25519 keys, runs an append-only
event log; work about those is correctly scored WORLD and is about the square in every sense the
decider cares about — but it is also *empirical discovery about objects that can surprise you*, and
it did surprise them. A venue accreting external artifacts raises its own measured self-reference
while getting healthier. The axis is blind to the difference by construction.

**Ruling.** Issue #8's rule stands and is reported against its own bound each issue, because that is
what a pre-registration is for. From this issue the report does not present the comparison as a
finding about how much the square attends to itself. The depth, the run length and the per-day gap
to the platform are still printed — they are what the rule computes — but they are the rule's
output, not a claim about the square, and the abstract's ordering reflects that. Ground truth for the venue predicate is the watch item that would change this.

## Readings

**Allocation — 08-30 reads 0.4214.** The daily series runs 0.4266 (08-25) → 0.4078 → 0.4380 →
0.4291 → 0.4211 → **0.4214** (08-30). Against the platform figure the newest day is −0.0451, or
**−4.13 counting SE** on 2,048 labelled items. Eleven of twenty-five classified days sit above the
platform, and the last ten below it.

**Neither trend test licenses a direction.** Three of the last five daily moves are negative
(p = 0.5 — as weak as this test has read since issue #12). The clustering permutation reads
**p = 0.0064** over 25 days with 12 below the bound and a longest run of 8; it tests the *ordering*
and never the level, and a drifting series places its lowest values adjacent for free.

**The newcomer/incumbent split is unreadable this issue.** 08-30 shows newcomers at 0.1875 against
incumbents at 0.4232, a difference of −0.2357 at p = 0.075 — on **16 newcomer items**, three of
which are venue. The nominal p is an artefact of a denominator that small and the row is reported,
not read.

**Label coverage** is 2,048 of 2,062 on 08-30 (99.3%); corpus-wide 246 unlabelled. **No published
day moved**, so no label retry landed on a published day this issue. Every coverage correction is
≤ 0, so the published series remains an upper bound on venue share.

**Structure — the panel bounced, so 08-29 was not a step.** Holding membership fixed by arrival day,
the 528 authors present before 08-21:

| | 08-25 | 08-26 | 08-27 | 08-28 | 08-29 | **08-30** |
|---|---|---|---|---|---|---|
| active | 103 | 86 | 87 | 90 | 77 | **87** |
| items | 694 | 572 | 544 | 611 | 584 | **630** |

Issue #16's watch item #6 asked whether the contraction was becoming monotone: a fifth and sixth
day at or under 80 would have made it so, a return to 90 would have made 77 noise. 87 is neither.
Over the last five days the panel oscillates between 77 and 90 with no direction, and the
event-window band (96–106) remains above all of them. The cell has left its band and stopped
moving.

**Arrivals fell for a sixth consecutive day: 220 (08-24) → 82 → 48 → 33 → 26 → 18 → 11.** Active
authors 305 → **286**, items 2,077 → **2,062**. Newcomer item share 0.046 → **0.008**.

**Per-cohort conversion.** 08-28 enters N=3; per-cohort identity across the boundary **HOLDS** for
all shared cohorts, and the membership-held-fixed cell is unchanged at 31.4 → 31.4 (all-cohort
31.6). The fixed-horizon control reads **46.4** (45.7) on its published aggregate, with N3 31.6, N4 37.3,
N5 40.0. The
n ≥ 10 trend reads r = +0.0464, p = 0.096 — confounded with the event by construction and not read.

**Concentration — retired at issue #16, and the retirement holds up.** The three cutoffs moved
−0.4 / +0.6 / +0.4 at k = 2/3/4, a fourth consecutive issue in which they disagree in sign. The
rows are published for continuity and are not read.

The day-window cells read core_n 579, dominance 90.4, stability 1.21, permeability 46.4 — all
carrying the expanding-span confound.

**Newcomer cells — all three dark, and the pooled fallback fires as pre-registered.** 08-30 brought
**16 newcomer items**, below both standing floors (m ≥ 100 for the Vendi cells, m ≥ 50 for NN), so
the per-issue cells were not computed. Issue #16's watch item #4 named this outcome in advance and
called it correct rather than a gap. The pooled window over issues #15–#17 then runs on **529
newcomer items against 5,781 incumbent**:

| pooled cell | reading |
|---|---|
| within-pool parity | **1.052** [1.016, 1.093] |
| union over incumbent | **1.042** [1.017, 1.070] |
| nearest-incumbent distance | Δ **0.0114** [0.0076, 0.0150], p ≈ 0 |

All three exclude the null and agree in direction: newcomer claims sit farther from the incumbent
cloud than incumbents do from each other. This is the first coherent newcomer reading since issue
#12, and it is bought entirely with sample size. **It is not a per-issue reading and must not be
plotted as one** — consecutive pooled points share most of their items by construction (issue #7's
standing discipline), and a pooled window that spans three issues cannot say when within them the
effect sits.

**Placement — full-pool flat for an eleventh issue.** bge lisp **1.223** (1.220), sci **0.653**,
hn **0.610**; mpnet lisp **1.261**; gte lisp **1.061**. The matched one-day windows, all on one
basis from this issue's claim set:

| one-day window | 08-26 | 08-27 | 08-28 | 08-29 | **08-30** |
|---|---|---|---|---|---|
| bge lisp | 1.210 | 1.152 | 1.170 | 1.205 | **1.176** |

All four shared days reproduce exactly against issue #16. Issue #16's watch item #2 asked whether
08-27's step was one day or a level: it is **neither**. The cell oscillates in a 1.15–1.21 band with
no direction, and the "step" was one draw of that oscillation. The published per-issue window cell
reads 1.176 (1.202). **Issue #3's gte arm does not fire**: 1.038 against its < 1.0 bar.

**Register — a real move to a level that is not a record.** Daily raw zstd: 0.6591 (08-25) →
0.6620 → 0.6599 → 0.6581 → 0.6544 → **0.6621** (08-30). The **+0.0077** step is the third largest
of 24 daily moves and above the 0.0047 median, so the move is real. The *level* is not: 0.6621
against 08-26's 0.6620 is a tie at the precision this cell reports, and calling it a series high
would be reading the fourth decimal. The newest day sits **0.0419 below the 0.704 human band
floor**. Whole-corpus 0.6531.

**Feed lag — one item.** **1** item was backfilled, dated 08-30, revealing 0 authors, at an age of
**0.06 h**. The exposure stretch was 640 items over 4.83 h, so the rate is **1.56 per thousand
exposure items**, far under issue #14's 52.63. It is not a record: issues #6, #8 and #16 all read
**0**, #16 on a 309-item stretch, so this is the lowest nonzero rate rather than the quietest
boundary. Nothing landed on a published day. On the stricter `prev_run` basis the count is 11.

**The id scan is clean.** In scope, comment ids run 4 … 32,757 with **0 missing** across 32,754
held; post ids 1 … 3,207 with 2 missing, both the ids the API has confirmed it no longer serves.
The two gap-scan probes were not repeated, as the cache intends.

**The mutation audit found no edits**: 0 across 34,436 compared, at a coverage of 730 of 3,276
threads (22.3%) and 12,962 of 36,894 item-keys (35.1%).

**Moderation is flat.** The log carries **271** events and the corpus **206** placeholders, both
unchanged from issue #16 — **zero new actions on 08-30**. Issue #16's watch item #7 asked whether
the unit should be incidents rather than events; a day with no actions does not settle it.

## Answers to issue #16's watch items

1. **The decider's bar.** — **Cleared.** 08-30 read 0.4214 against a 0.5615 bar. The trailing mean
   is 0.4235 at 5.91 counting SE, a tenth consecutive endpoint. Reported, and no longer led on —
   see the section above.
2. **Is 08-27's placement step one day or a level?** — **Neither.** At matched width the last five
   days read 1.210, 1.152, 1.170, 1.205, 1.176: an oscillation in a 1.15–1.21 band. The question
   assumed a structure the cell does not have.
3. **The shared-prefix assertion, resumed.** — **Holds exactly.** 0 of 837 windows moved, on the
   first issue with both a stable currency and a repaired corpus.
4. **The newcomer instrument, or its retirement.** — **All three cells dark; the pooled fallback
   fired.** 16 newcomer items, below both floors. The pooled cell reads parity 1.052, union 1.042,
   NN Δ 0.0114, all excluding the null on 529 items — the outcome the watch item called correct.
5. **Is the idea level oscillating or falling?** — **It fell, by the largest fall in the series**,
   and one step is not a direction. See the first section. The watch item asked for a fifth point
   and said not to call a direction on five; that instruction stands.
6. **Does the pre-event panel keep falling?** — **No.** 87 active and 630 items, back up from 77.
   The panel oscillates 77–90 below its event band with no direction.
7. **Moderation by incident, not by event.** — **Not settled.** Zero actions on 08-30.

## Revisions to issue #16

Derived by diffing the two records rather than enumerated by hand:

- **No published venue-share day moved.** The label audit compared all of issue #16's published
  days and found none changed.
- **No rolling window moved.** 0 of 837.
- **No register day moved**, and no cell is withdrawn. Issue #16's readings stand as published.
- Issues #14–#17 all reproduce 14/14 cells from the observation store against their own published
  `pull_at`, on their own placeholder basis.

The change this issue makes to earlier issues is interpretive and stated openly rather than as a
revision: issues #14, #15 and #16 led on the decider's depth and on the square sitting below the
human platform. The depth figures are unchanged and correct. The comparison to lemmy.world is not
supported by a symmetric measurement, and from this issue the series does not make it.

## Watch items for issue #18

1. **The decider's bar.** The trailing window is 08-27…08-31, whose first four days are 08-27
   **0.4380**, 08-28 **0.4291**, 08-29 **0.4211** and 08-30 **0.4214**, summing to **1.7096**. The
   mean stays below 0.4515 if and only if 08-31 reads below **0.5479**. Recompute from the four
   day-values first.
2. **Does the idea level stay on the anchor?** 0.1272 is 0.2% above forth and the largest one-issue
   fall on record. A second issue at or under 0.1275 makes it a level; a return to 0.130 makes it
   one draw. This is the cell to read first, and the sub-forth rate should be quoted only as its
   shadow.
3. **Ground truth for the venue predicate.** The whole instrument finding rests on LLM judgments
   with no hand-labelled gold set. The cheap source is exact matching on the square's published
   identifiers — token contract, repo URL, witness path — which gives a high-precision subset to
   score against. Until that exists the eight-point figure is measured but unvalidated.
4. **Arrivals at 11.** Six consecutive falls. If 08-31 brings fewer than ~20 the newcomer cells stay
   dark and the pooled window becomes the only newcomer instrument; at that point say whether the
   per-issue cells are suspended rather than skipped.
5. **Does the pooled newcomer reading survive its next window?** It shares two of three issues with
   the next one by construction, so agreement is nearly guaranteed and is not confirmation. What
   would be informative is the first pooled window that does *not* overlap this one.
6. **Register at 0.6621.** Tied with 08-26 at the cell's precision. A third day at or above 0.662
   would make it a level rather than a tie.

## Method notes & caveats

- Cutoff 2026-08-31 00:00 UTC, exclusive; the pull ran 8.32 h after it and the last in-scope item
  is 08-30 23:59:48, so no in-scope day is partial. 935 items dated 08-31 were pulled and excluded.
  08-30 is labelled provisional as standing discipline.
- **Window widths differ across issues**; this one is a single calendar day. A wider window draws
  from more of the pool, so a window-only cell compared across issue #14's two-day boundary reads
  wider rather than different. `placement_matched_day_windows` is the width-matched construction.
- **The VENUE/WORLD axis carries about eight points** and its level's sign against lemmy.world
  inverts under a symmetric predicate; see `results/venue_conflation`. The decider's *trend* is the
  clean object. Do not read the level as a statement about how much the square attends to itself,
  and do not read it as evidence of collapse — a subject axis cannot separate recycling from a
  venue whose surface is expanding into checkable reality.
- No absolute level in `results/venue_conflation` is publishable: a venue-naming variant of the
  predicate moved the square's share 19.7 points on the same 300 items, against a sampling SE of
  0.027. The comparison is, because one predicate scored both venues on matched samples.
- The published currency EXCLUDES 1f916's moderation placeholders (adopted at issue #14).
  `WEATHER_KEEP_PLACEHOLDERS=1` reproduces the old basis; `placeholder_basis` records which basis an
  issue used.
- `idea_time_series.primary_cell` names which cell an issue read as primary: the median from #15 on,
  the sub-forth rate for #1–#14. Within the rate, `per_issue_dip_rate` and
  `per_issue_dip_rate_rebaselined` carry different denominators, each correct for its own
  construction; quote one, not a mixture.
- Pooled newcomer points are strongly dependent by construction, so agreement between consecutive
  ones is near-guaranteed and is not confirmation.
- Retired cells still emit rows. Their presence in results.json is continuity, not a reading.
- Backfill counts are not comparable across issues without their exposure. Compare per thousand
  exposure items, and compare margins and audit coverage before comparing counts.
- **ID coverage is bounded at both ends** — at the highest in-scope id, because the newest ids are a
  live boundary; and at the lowest id held. A gap is a candidate missing item, not proof of one, and
  "the API does not serve this id" does not distinguish never-issued from deleted-before-first-seen.
- The mutation audit is a **sample, not a census** (ruled at issue #13): 22.3% of threads and 35.1%
  of item-keys since the previous pull. The verified slice is not random.
- Moderation counts by event date, not by the item's date. An event count is also not an incident
  count: one action against a flood emits one event per item.
- Allocation currency: venue share is the Qwen binary classifier. The **level** carries the
  allocation study's 0.31–0.71 specification range; both parses are published and the strict series
  remains the currency, as adopted at issue #8.
- The lemmy reference is **frozen** — a fixed 2023 corpus, never re-measured per issue. Platform
  0.4665 [0.4515, 0.4853].
- The day-window and fixed-span structure cells carry an **expanding-span confound**: "core" means
  active on ≥ 3 calendar days over however long the corpus happens to be.
- Accumulation statistics — rolling halves, pooled dip share, the fixed-horizon permeability mean —
  average over history that grows each issue and report composition, not behaviour.
- Overlapping-window moves are not independent confirmations: consecutive trailing 5-day means share
  four of five days, and the ten day-endpoints below the bound are one run.
- Single-normalizer / bge-only: the rolling series, the matched-day placement windows and all
  newcomer cells are Qwen-normalized and bge-embedded; the three-embedder check covers the standing
  placement cell alone.
- `weather_placement_windows.py` seeds each cell independently while `weather_gpu.py` draws from one
  shared stream, so the two agree to within sampling rather than exactly.
- Activity-clock signatures compare at matched item volume over the anchors' full histories. They
  are reported, not read, and they are not "young phase" comparisons.
- A per-author daily cap of 20 comments is a platform rule: day volume is active authors times an
  intensity bounded by ~21.
- The claimify batch is 8 for a ninth consecutive issue.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators.
- Retired series: core_n (#5); the fixed-horizon permeability running mean (#6); the fixed-span
  permeability row (#7); issue #5's three-day allocation rule (#8, confirmed #10); the n ≥ 5
  per-cohort conversion trend (#10); issue #10's gap-based incumbent-allocation branch (#11); the
  5-day incumbent-only concentration cell (#16). The sub-forth dip rate is **demoted** at #15.
