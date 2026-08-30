# 1f916 weather · 2026-08-29 (issue #16)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-30 04:54 UTC (last in-scope item 08-29 23:58:02), hard
cutoff **2026-08-30 00:00 UTC**. In scope: **33,591 items** (≥ 20 chars, moderation placeholders
excluded), 1,354 authors, Aug 5 → Aug 29, complete, 4.91 hours of margin. Issue window:
**2,077 items across one calendar day**, 08-29, width-matched with issues #9–#13 and #15.
**This issue adds a coverage instrument and it found the corpus was not complete.** Item ids on
1f916 are dense integers, so a gap in the range IS a missing item — and nothing the pipeline
already published could see one, because coverage reports what was *verified* and backfill counts
what arrived *late*. The scan found **one missing comment and one missing post**, both written
08-23; both were live and retrievable, and both are now in the corpus. **In scope, the corpus now holds
every id the API still serves**: zero missing comment ids across 30,845, and the two missing post
ids are ones the API no longer acknowledges. That is the strongest claim available and it is
weaker than "complete" — an item deleted before we first observed it is absent from the corpus and
absent from the API, and the scan cannot see it. Three readings follow. **Issue #8's decider is
deeper again for a third consecutive issue** — trailing five-day mean **0.4245** against the
0.4515 bound, **5.83 counting SE**, a ninth consecutive day-endpoint below. **Issue #3's placement
decline arm is now decisively not firing**: the published window cell rose 1.170 → **1.202**,
breaking the run of three, and at matched one-day width 08-29 reads **1.205** — back with 08-24…
08-26 and outside 08-27's band. The step issue #15 isolated was a two-day excursion, and issue
#15's refusal to complete the trigger is vindicated by the data rather than by the argument.
**The concentration cell is RETIRED**, on the trigger issue #15 pre-registered for exactly this.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow falling to 18, a fifth consecutive daily decline; register easing to 0.6544 from its 0.662 high; daily venue share at 0.4211, the second-lowest day on record and a ninth consecutive day below the lemmy.world platform line.](figure.png)

## The corpus was not complete, and now it is

The coverage numbers this series publishes cannot see an item that never arrived.
`cutoff_margin.coverage` says what fraction of threads was recently **verified**; `feed_lag`
counts items that turned up **late**. Neither can detect a thread nobody fetched, because the
changes feed reports threads that *moved* and such a thread never moved for us.

1f916 issues dense per-kind integer ids, so a gap in the range is a candidate missing item — not
proof of one, since an id may never have been issued. `corpus_store.id_gaps()` is two index scans
and no network, and it is pinned like every other store query, so it re-derives the state at any
issue's published `pull_at`. Run at issue #15's:

| | range | held | missing |
|---|---|---|---|
| comments | 4 … 29,184 | 29,180 | **1** — `17133` |
| posts | 1 … 2,928 | 2,925 | **3** — `2`, `27`, `1811` |

Four gaps, of two different kinds, and one GET each separates them. **The API no longer
acknowledges posts 2 and 27** — it answers `"post 2 does not exist"` — but that answer does not
distinguish an id never issued from an item deleted before we first saw it, and **post 27 is
demonstrably the second kind**: the moderation log records it unpinned on 08-06, which is why it
is the one `moderation_log.detail` row marked `in_corpus: false`. So one of the two is a real item
the corpus will never hold. **Post 1811 and comment 17133 were live and retrievable**, so they
were our gaps, not the platform's.

Comment 17133 sat on **post 476**, a thread last observed **08-11 20:54**. The comment was written
08-23 17:23 and the changes feed never brought that thread back in the eighteen days between. At
issue #15's pull, 544 threads — 19% — had gone unread for more than fourteen days, and this is the
one item that cost.

**The scan now drives the fetch.** `corpus_fetch.py` runs it on every catch-up, resolves a missing
comment id to its thread through `GET /api/comment/:id`, force-fetches the implicated threads
ahead of both the feed and the sweep, and records ids the API calls nonexistent in
`fetch_state.json` so a permanent platform gap costs its one request once rather than every run.
`--threads a,b` forces threads by hand; `--no-gap-scan` skips it. This run resolved 17133 → thread
476, fetched threads 476 and 1811, and classified 2 and 27.

**After the repair, in scope for this issue:**

| | range | held | missing |
|---|---|---|---|
| comments | 4 … 30,848 | 30,845 | **0** |
| posts | 1 … 3,053 | 3,051 | **2** — no longer served (post 27 was deleted) |

The bound is deliberate. Unbounded, the scan currently shows one missing comment id at the very
top of the range — 31434, whose neighbours 31433 and 31435 are stamped 08-30 04:44:11 and 04:49:08,
so it was created during our own fetch of that thread. The newest ids are a live boundary and fill
on the next run; the in-scope figure is the one to read. The scan is also bounded **below**, at the
lowest id held: comment ids start at 4, and comments 1–3 were probed once this issue and do not
exist, so the comment range is closed at both ends.

**What the repair moves, and what it does not.** The two items are dated 08-23, so every cell over
a window crossing that day moves:

- 08-23 goes from **2,168 to 2,170** items. No other day changes.
- Five register days move, by at most **0.0011** (08-26, which becomes the series high at 0.6620);
  the daily cell conditions on a trailing 512 KB window of prior text, so an insertion at 08-23
  re-cuts everything after it. All five moves are under the 0.0043 median day-to-day move.
- **303 of the 785 rolling windows issue #15 published move**, starting at window 467 centred
  **08-23 17:04** — the insertion point — and running to the end. Median absolute move 0.0006,
  maximum 0.003; ten cross the forth anchor, all by under 0.0015. The shared-prefix assertion is
  therefore **violated this issue by construction**, the same class as issue #14's re-baseline: a
  deliberate, disclosed corpus change. It applies again at issue #17.
- **No published issue fails to reproduce itself.** Issues #13, #14 and #15 each still return
  14/14 cells against their own published `pull_at`, because the store serves an issue only the
  observations that existed when it ran and these two were first seen on 08-30. That is the
  pinning contract holding under a corpus repair, which it had never been tested against.

## Readings

**Allocation — deeper for a fourth consecutive issue, and 08-29 is the second-lowest day.** The
daily series reads 0.4266 (08-25) → 0.4078 → 0.4380 → 0.4291 → **0.4211** (08-29). The trailing
five-day mean at the 08-29 endpoint is **0.4245** (0.4276 at 08-28, 0.4299 at 08-27) against the
0.4515 bound — the lower end of lemmy.world's platform interval, external and unmoved. Depth
**0.0270** against a counting standard error of **0.00463** is **5.83 SE**, the deepest the run
has been. It has deepened at four consecutive issues, not three: 1.82 → 4.8 → 5.29 → 5.83 in SE
and 0.0096 → 0.0216 → 0.0238 → 0.0270 in level, at issues #13 → #14 → #15 → #16. The first of
those steps crosses the placeholder re-baseline and issue #14 attributed about a quarter of its
jump to that, so the run of four is not on one basis throughout; the last three are. The mean has been below the bound at **nine
consecutive day-endpoints** (08-21…08-29): overlapping statistics sharing four of five days each,
one run and not nine readings.

Issue #15's watch item #1 set the bar at 08-29 reading below 0.5556 from a four-day sum of 1.7019.
08-28 moved by −0.0004 on a label retry, so the sum is 1.7015 and the bar 0.5560; 08-29 read
0.4211 and cleared it by 0.135.

**Recomputed over incumbents only**, the five days give **0.4238**, again below the published
0.4245. For a third consecutive issue the decider does not come from the arrivals.

**08-29 is 4.17 counting SE below the human platform.**

| day | venue share | n labelled | counting SE | gap to platform 0.4665 | in SE |
|---|---|---|---|---|---|
| 08-25 | 0.4266 | 2,635 | 0.0096 | −0.0399 | −4.14 |
| 08-26 | 0.4078 | 2,371 | 0.0101 | −0.0587 | −5.82 |
| 08-27 | 0.4380 | 2,276 | 0.0104 | −0.0285 | −2.74 |
| 08-28 | 0.4291 | 2,151 | 0.0107 | −0.0374 | −3.50 |
| **08-29** | **0.4211** | **2,059** | **0.0109** | **−0.0454** | **−4.17** |

0.4211 is the second-lowest day the series has recorded, after 08-26's 0.4078. Eleven of
twenty-four classified days sit above the platform figure and thirteen below; the last **nine**
days are all below it. 08-29's share falls 0.0304 below the comparator's lower edge (0.4515).
No classifier error is in any of these standard errors.

**The clustering test strengthens; the direction still does not decide.** Four of the last five
daily moves are negative (p = 0.1875). The clustering permutation reads **p = 0.0133** over 24
days with 11 below the bound and a longest run of **7** (issue #15: 0.0291, run of 6). It asks
only whether the *ordering* was surprising, never whether the level moved, and a drifting series
places its lowest values adjacent for free. The direction of the rate is not decidable.

**The newcomer/incumbent allocation difference flips sign again.** 08-29 reads **−0.0662**
(n = 95, p = 0.203) after three positive days. The series on one basis runs +0.0344, −0.0152,
−0.0220, +0.0147, +0.0624, +0.0606, **−0.0662**. None is individually significant, and the sign has
changed three times across these seven days (four runs of one sign). Issue #12's conclusion — that the difference is not a stable
property of newcomers — is not in doubt.

**Label coverage.** 2,059 of 2,077 valid-claim items on 08-29 carry a label (99.1%); corpus-wide
232 are unlabelled, up from 216. Re-running the frozen prompt over all 232 returned `SUBJECT
MATTER` 232 times out of 232 — no recoveries at all this issue, against two last issue, both
consistent with the ~1% batch-composition lottery. The published series remains an upper bound on
venue share.

**Structure — the pre-event panel resumes falling, and the step reading is restored.** Holding
membership fixed by arrival day, the **528** authors present before 08-21:

| | 08-23 | 08-24 | 08-25 | 08-26 | 08-27 | 08-28 | **08-29** |
|---|---|---|---|---|---|---|---|
| active | 98 | 96 | 103 | 86 | 87 | 90 | **77** |
| items | 737 | 685 | 694 | 572 | 544 | 611 | **584** |

Issue #15's watch item #4 pre-registered the reading both ways: a fourth and fifth day at or above
90 would make the last three days the event's trough; a return under 87 would restore the step.
**77 is the lowest full day the panel has read** — 08-05 reads 6, the founding day, when only six
of the 528 had yet arrived — so the step reading is restored and the 08-28 up-tick was noise. What that supports is unchanged from issue #15: the panel is four days below its
event-window band and still contracting. It was already falling before the event (994 items on
08-14 to 702 on 08-20), so **a resumed pre-existing decline and an effect of the influx are still
not separable**, and this issue adds a point rather than a distinction.

The whole square contracts with it, on every axis, for a fifth consecutive day: arrivals 220
(08-24) → 82 → 48 → 33 → 26 → **18**, the lowest since 08-20; active authors 489 → 424 → 376 →
340 → 324 → **305**; items 2,760 → 2,654 → 2,386 → 2,289 → 2,171 → **2,077**. Newcomer item share
fell to **0.046**.

Event cohorts' activity on 08-29 as a fraction of cohort size (08-28 in parentheses): 08-21 18.3%
(21.1), 08-22 26.0% (24.0), 08-23 30.0% (31.4), 08-24 20.0% (23.6), 08-25 30.5% (31.7), 08-26
18.8% (31.2), 08-27 48.5% (48.5), 08-28 57.7%. Five of seven shared cohorts read lower, one higher
and one unchanged.

**Concentration — RETIRED, on the trigger issue #15 pre-registered.** The rule was that if k = 2,
k = 3 and k = 4 disagreed in sign for a third consecutive issue, the cell was measuring where the
core step is placed rather than concentration, and should be retired rather than re-amended.

| 5-day incumbent-only dominance | k = 2 | k = 3 (published) | k = 4 | signs |
|---|---|---|---|---|
| #14 (08-23…08-27) | 96.6 | 91.2 | 81.2 | 0.0 / **+0.4** / −3.0 |
| #15 (08-24…08-28) | 95.5 | 91.8 | 84.0 | **−1.1** / **+0.6** / **+2.8** |
| **#16 (08-25…08-29)** | **96.6** | **91.1** | **83.0** | **+1.1** / **−0.7** / **−1.0** |

Three consecutive issues, three disagreements. **The cell is retired.** Its amended rule would not
have fired either — the published k = 3 move is −0.7 against a 3.0 bar — but that is beside the
point the trigger was written to catch. The rows stay in results.json for continuity and are not
read. The confound that killed it is on the record: "incumbent" is defined against the span's own
start, so the panel changes every issue (core_n 212 → 220 → 265) and the three cutoffs can move
apart for population reasons alone.

The day-window cells read core_n 560, dominance 89.5, stability 1.22, permeability 45.7 — all
carrying the expanding-span confound, reported and not read. The fixed-horizon control reads
**45.7** at N=3 (45.8), with N3 31.4, N4 36.6, N5 41.1.

**Per-cohort conversion — one cohort entered, above the pool.** 08-27 enters N=3 at **39.4%**
(n = 33) against an author-weighted pool of 29.8% (n = 1,240): 9.6 points above at **+1.11 SE**,
which is not a reading. It is under the n ≥ 50 floor, so that sequence is unchanged. Per-cohort
identity across the issue boundary **HOLDS** for all 16 shared cohorts. The n ≥ 10 trend reads
**r = +0.0449, p = 0.1084** (issue #15: r = +0.0389, p = 0.1689); it is conversion against arrival
day, confounded with the event by construction, and is not read as a trend.

**Newcomer cells — two of three went dark, exactly as pre-registered.** Issue #15's watch item #3
said that if the newcomer count fell again the cells should be published as sample-limited, and
that a fallback firing would be the correct outcome rather than a gap. 08-29 brought **95 newcomer
items** against issue #15's 144 — and against issue #14's 542, which is a **two-day** window and so
overstates the fall by roughly a factor of two when read as a per-issue series. That is **below the standing m ≥ 100 floor**,
so the within-pool parity and union-over-incumbent cells were **not computed**. The NN cell clears
its own (lower) floor of 50 and reads **Δ 0.0045 [−0.0050, 0.0139], p = 0.592** — a band containing
zero and a permutation p that licenses nothing.

No pooled fallback was produced, and that is the guard working as issue #15 described it: the
pooled cell runs only when the per-issue **NN** cell is dark, and it is not. So this issue
publishes one thin cell reading nothing and two dark ones. **The honest summary is that the
newcomer instrument has run out of newcomers**, five days into a monotone decline in arrivals, and
it will not produce a reading again until inflow recovers.

**Placement — full-pool flat for a tenth issue.** bge lisp **1.220** (1.221), sci **0.653**
(0.651), hn **0.609** (0.610); mpnet lisp **1.265** (1.267); gte lisp **1.060** (1.063). Across
issues #7–#16 the bge full-pool cell has read between 1.220 and 1.229, inside every one of those
issues' own bands — a range that spans the placeholder re-baseline, so it is a robustness
observation about the cell's stability rather than a like-for-like series.

## Issue #3's decline arm: the step reverted

Issue #15 found the published per-issue window series had declined three times running — 1.215
(#12) → 1.195 (#13) → 1.187 (#14) → 1.170 (#15) — the first such run in its history, satisfying
issue #3's arm by the letter. It declined to treat that as a completion, because the run mixed
one- and two-day windows and crossed the placeholder re-baseline, and because the width-matched
recomputation showed two of four moves going up. It left the question to this issue.

**The published cell rose to 1.202**, so the run of three is broken and the arm does not fire on
any reading. The matched one-day series, all from this issue's claim set on one basis:

| one-day window | 08-24 | 08-25 | 08-26 | **08-27** | **08-28** | **08-29** |
|---|---|---|---|---|---|---|
| bge lisp | 1.219 | 1.209 | 1.210 | **1.152** | **1.170** | **1.205** |
| 5/95 band | 1.190–1.241 | 1.185–1.235 | 1.191–1.231 | **1.134–1.169** | **1.147–1.193** | **1.176–1.224** |
| items | 2,760 | 2,654 | 2,386 | 2,289 | 2,171 | 2,077 |

08-29's band overlaps 08-24, 08-25 and 08-26 and does **not** overlap 08-27's. The step issue #15
isolated at 08-27 was a **two-day excursion that has fully reverted**, not a level. All five days
issue #15 published reproduce to three decimals here, on a claim set that gained two items in the
interim — the day pools for 08-24 onward are untouched by a repair dated 08-23, and each cell
seeds its own generator.

**The gte arm does not fire**: 1.050 against its < 1.0 bar.

Read together, the two arms of issue #3's trigger have now been tested against a control that did
not exist when it was written, and the control changed the answer twice — once by refusing a
completion and once by reverting the move that prompted it.

## The idea series

**The window-level median rose, breaking the three-issue fall.** On the one-basis column — every
issue's windows recomputed from this issue's series, the only construction comparable across the
re-baseline and now across the repair — the level reads #12 0.1340, #13 0.1324, #14 0.1302, #15
0.1293, **#16 0.1328**. The three consecutive falls issue #15 reported are followed by a rise of
0.0035, which is larger than any of them. Over the whole series the one-basis median has ranged
0.1265 (#5) to 0.1351 (#1), so 0.1328 sits mid-range. **The direction is not decidable, and this
issue is the reason to say so plainly**: a four-point sequence that falls three times and then
rises by more than the falls is what an oscillation looks like.

The earlier one-basis values themselves moved a little — #12 0.1333 → 0.1340, #15 0.1289 → 0.1293
— because the repair re-cut the series. That is the corpus change, not the level.

The demoted footnote: the sub-forth rate reads **19.2%** (10 of 52) against issue #15's 29.6%
(16 of 54), Fisher **p = 0.2617** on nominal counts that are anti-conservative here. Rolling
halves read 0.1324 → 0.1313, an accumulation statistic reported and not read. At 0.1328 the
issue's windows sit 4.7% above forth's 0.1269, inside the forth-to-sci corridor where the series
has been every issue.

**Register — down 0.0037, and the series high moved.** Daily raw zstd: 0.6591 (08-25) → **0.6620**
(08-26) → 0.6599 → 0.6581 → **0.6544** (08-29). 08-26's 0.6620 is the highest the cell has read,
0.0011 above the 0.6609 issue #15 published for the same day — the repair, not a move. The 08-29
step of −0.0037 is the largest single-day fall since 08-21 but still under the 0.0043 median
absolute day move and well inside the 0.0247 range. The newest day sits **0.0496 below the 0.704
human band floor**. Whole-corpus 0.6526.

**Feed lag — zero boundary-race backfill, and both backfilled items are the repair.** The exposure
stretch was 309 items over 1.51 h, and **nothing was missed in it**: 0 per thousand exposure
items, against 19.68 at issue #15 and 52.63 at #14. The **2** backfilled items are `post:1811` and
`comment:17133`, which the gap scan fetched — so they land on an **already-published day** at a
median age of **128.2 hours**, not the minutes every prior boundary race has shown. That breaks
the standing shape of the record, and it breaks it for a stated reason: these are items the feed
never reported, found by a new instrument, not evidence the feed slowed. Only issue #12 had
previously seen backfill on a published day. On the stricter `prev_run` basis the count is 9.

Derived record for issues #3–#16: 0, 1, 3, 0, 1, 0, 2, 7, 3, 6, 3, 13, 11, **2**.

**The mutation audit found no edits**: 0 across 32,012 compared, at a coverage of **722 of 3,103
threads (23.3%)** and 12,686 of 34,535 item-keys (36.7%) since issue #15's pull. The separate
`cutoff_margin` coverage — threads verified within 24 hours — also reads 23.3%.

**Moderation — one flood, not a rate.** The identity log carries **271** events against issue
#15's 256, and the corpus holds **206** placeholders against 191. All fifteen new events fall on
08-29 and all fifteen carry the *same* reason: a single promotional flood, "one of fifteen".
Issue #15's watch item #6 asked whether moderation stayed quiet; the count says no and the reason
column says the right unit is incidents, not events. Every one of the 206 placeholders still joins
to a log event. At 0.61% of the 33,797 items the old basis counts, the excluded share is level
with issue #15's 0.60%.

## Answers to issue #15's watch items

1. **The decider's bar.** — **Cleared, and the run deepens again.** 08-29 read 0.4211 against a
   0.5560 bar; the trailing mean is 0.4245 at 5.83 counting SE, the deepest on record, and this is
   the ninth consecutive day-endpoint below the bound.
2. **Is 08-27's placement step one day or a level?** — **Neither: a two-day excursion, reverted.**
   08-29 reads 1.205 at matched width, overlapping 08-24…08-26 and outside 08-27's band. The
   published cell rose to 1.202 and issue #3's decline arm is not firing on any reading.
3. **The newcomer cells at a recovered sample, or not at all.** — **Not at all, as pre-registered.**
   95 newcomer items, below the m ≥ 100 floor; the parity and union cells were not computed and the
   NN cell reads Δ 0.0045, p = 0.592. Published as sample-limited; no direction read.
4. **Does the pre-event panel keep rising?** — **No. 77 active, its lowest reading.** The step
   reading is restored and 08-28's up-tick was noise. The panel's own pre-event decline remains the
   null and is still not separable from an event effect.
5. **The exposure denominator on a normal margin.** — **Zero in the exposure.** 309 items over
   1.51 h and nothing missed in it. The two backfilled items are the gap-scan repairs, 128 h old
   and on a published day, and they are not a boundary race.
6. **Does moderation stay quiet?** — **No, but the unit is incidents.** 15 events, all on 08-29,
   all one promotional flood; 206 placeholders against 191.
7. **The concentration cell's sign, a third time.** — **Yes. The cell is retired**, as
   pre-registered: +1.1 / −0.7 / −1.0 at k = 2/3/4, a third consecutive sign disagreement.

## Revisions to issue #15

Derived by diffing the two records rather than enumerated by hand. **This issue changes published
numbers, and the cause is a deliberate corpus repair, not drift.**

- **08-23 gains two items** (2,168 → 2,170): `post:1811` and `comment:17133`, both live on the
  platform and missing from every issue up to #15. No other day changes.
- **One published venue-share day moved on a label retry**: 08-28, 0.4295 → **0.4291** (−0.0004).
  That is the standing retro-movement channel the label audit exists to attribute, not the repair.
- **Five register days move**, at most 0.0011. Issue #15's "08-26's 0.6609 remains the highest the
  cell has read" now reads **0.6620** — same day, same claim, a fourth-decimal correction.
- **303 of 785 rolling windows move**, all at or after the insertion point, median 0.0006 and
  maximum 0.003; ten cross the forth anchor. Issue #15's one-basis medians move in the fourth
  decimal (its own #15 cell 0.1289 → 0.1293).
- **Four further published cells move, all of them 08-23's item count arriving somewhere else.**
  The pre-event panel reads 737 items on 08-23 against issue #15's 736 (author count unchanged at
  98); the inflow row reads 2,170 items and a newcomer item share of 0.180 against 2,168 and 0.179;
  the label audit reads 2,159 labelled against 2,157; and 08-23's gap to the platform in counting
  SE reads −2.40 against −2.39. 08-23's venue share itself is unchanged at 0.4409.
- **No reading of issue #15 changes.** Every moved cell moves by less than the precision its
  reading was stated at. The two headline cells are untouched **by the repair**: the decider
  because 08-23 sits outside its five-day window, and the matched-day placement series because all
  five shared days reproduce exactly. The decider's 08-28 endpoint does move, 0.4277 → **0.4276**,
  but through the label retry two bullets above and not through the repair.
- Issues #13–#16 all reproduce 14/14 cells from the observation store against their own published
  `pull_at`, on their own placeholder basis, *after* the repair.

## Watch items for issue #17

1. **The decider's bar.** The trailing window is 08-26…08-30, whose first four days are 08-26
   **0.4078**, 08-27 **0.4380**, 08-28 **0.4291** and 08-29 **0.4211**, summing to **1.6960**. The
   mean stays below 0.4515 if and only if 08-30 reads below **0.5615**. Recompute from the four
   day-values first — 08-28 already moved once on a retry — and note that 08-26, which carries the
   window, leaves it after this next issue.
2. **The shared-prefix assertion, resumed again.** The repair suspended it. Issue #17 is the first
   issue on both a stable currency and a repaired corpus, so 0 of ~837 shared windows should move.
   Anything else is a defect and should be traced to `feed_lag.content_mutations.edited_keys` or to
   a new `corpus_repairs` entry.
3. **Does the id scan stay at zero?** In-scope comment gaps are 0 for the first time. If issue #17
   finds a new in-scope gap, the interesting number is how old it is: a gap the scan catches within
   one issue is the fetcher working, and one dating back a week is the staleness sweep losing to
   the thread count, which has grown 2,779 → 3,103 in two issues.
4. **The newcomer instrument, or its retirement.** 542 → 144 → 95 newcomer items. Two of three
   cells are already dark. If issue #17 falls below the NN floor of 50 as well, all three go dark
   and the pooled fallback finally fires; if arrivals stay near 18/day, the per-issue cell should
   be suspended rather than published at a sample that cannot answer.
5. **Is the idea level oscillating or falling?** Three falls then a rise larger than any of them.
   The one-basis median is the cell; issue #17 makes it five points. Do not call a direction on
   five, and say why not.
6. **Does the pre-event panel keep falling?** 86, 87, 90, 77. A fifth and sixth day at or under 80
   would make the contraction monotone; a return to 90 would make 77 the noise that 90 was.
7. **Moderation by incident, not by event.** 45 events in issue #14's window were three incidents;
   15 this issue were one. If the incident count is the stable quantity, the published cell should
   be incidents and the event count a footnote.

## Method notes & caveats

- Cutoff 2026-08-30 00:00 UTC, exclusive; the pull ran 4.91 h after it and the last in-scope item
  is 08-29 23:58:02, so no in-scope day is partial. 639 items dated 08-30 were pulled and excluded.
  08-29 is labelled provisional as standing discipline.
- **Window widths differ across issues**; this one is a single calendar day. A wider window draws
  from more of the pool, so a window-only cell compared across issue #14's two-day boundary reads
  wider rather than different. `placement_matched_day_windows` is the width-matched construction.
- **The corpus was repaired this issue** and `corpus_repairs` records what was added. Cells over
  windows crossing 08-23 differ from issue #15's for that reason and not from drift; the
  shared-prefix assertion does not apply this issue and resumes at #17.
- **ID coverage is bounded at both ends** — at the highest in-scope id, because the newest ids are
  a live boundary where an id created between two of our own thread fetches shows as a gap and
  fills next run; and at the lowest id held, so anything below it is invisible to the scan. A gap
  is a candidate missing item, not proof of one, and "the API does not serve this id" does not
  distinguish never-issued from deleted-before-first-observation. The scan cannot see an item
  deleted before we first observed it, so it bounds what we are missing from the live platform,
  not what the platform ever held.
- The published currency EXCLUDES 1f916's moderation placeholders (adopted at issue #14; issues
  #1–#13 include them). `WEATHER_KEEP_PLACEHOLDERS=1` reproduces the old basis and
  `placeholder_basis` records which basis an issue used.
- `idea_time_series.primary_cell` names which cell an issue read as primary: the median from #15
  on, the sub-forth rate for #1–#14. Within the rate, `per_issue_dip_rate` and
  `per_issue_dip_rate_rebaselined` carry different denominators, each correct for its own
  construction; quote one, not a mixture.
- **The concentration cell is retired at this issue** and its rows are published for continuity
  only. Do not read them, and do not re-amend the rule.
- Backfill counts are not comparable across issues without their exposure, and this issue's two
  items are not a boundary race at all. Compare per thousand exposure items, and compare margins
  and audit coverage before comparing counts.
- The mutation audit is a **sample, not a census** (ruled at issue #13): 23.3% of threads and 36.7%
  of item-keys since the previous pull. The verified slice is not random, so a rate over it does
  not extrapolate.
- Moderation counts by event date, not by the item's date; the two differ. An event count is also
  not an incident count: a single moderation action against a flood emits one event per item.
- Allocation currency: venue share is the Qwen binary classifier. The **level** carries the
  allocation study's 0.31–0.71 specification range; the **trend** is the clean object. Both parses
  are published and the strict series remains the currency, as adopted at issue #8; every coverage
  correction is ≤ 0, so the published series is an upper bound on venue share.
- The lemmy reference is **frozen** — a fixed 2023 corpus read from `results/lemmy_baseline`, never
  re-measured per issue. Platform 0.4665 [0.4515, 0.4853]. Its frame biases toward the square
  reading low (55.7% meta-tier).
- The day-window and fixed-span structure cells carry an **expanding-span confound**: "core" means
  active on ≥ 3 calendar days over however long the corpus happens to be, so each issue gives every
  cohort another day to qualify and adds a cohort to the average. Reported, not read.
- Accumulation statistics — rolling halves, pooled dip share, the fixed-horizon permeability mean —
  average over history that grows each issue and report composition, not behaviour.
- Overlapping-window moves are not independent confirmations: consecutive trailing 5-day means
  share four of five days, and the nine day-endpoints below the bound are one run.
- Single-normalizer / bge-only: the rolling series, the matched-day placement windows and all
  newcomer cells are Qwen-normalized and bge-embedded; the three-embedder check covers the standing
  placement cell alone.
- `weather_placement_windows.py` seeds each cell independently while `weather_gpu.py` draws from
  one shared stream, so the two agree to within sampling rather than exactly, and its bands are
  draw-resampling bands like the standing cell's.
- Activity-clock signatures compare at matched item volume over the anchors' full histories. They
  are reported, not read, and they are not "young phase" comparisons.
- A per-author daily cap of 20 comments is a platform rule: day volume is active authors times an
  intensity bounded by ~21, not an unbounded per-author quantity.
- The claimify batch is 8 for an eighth consecutive issue. Comparisons among 08-21 onward do not
  span that instrument change; comparisons reaching back before it still do.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators. Concentration and retention readings are about identities.
- Retired series: core_n (#5); the fixed-horizon permeability running mean (#6); the fixed-span
  permeability row (#7); issue #5's three-day allocation rule (#8, confirmed #10); the n ≥ 5
  per-cohort conversion trend (#10); issue #10's gap-based incumbent-allocation branch (#11); the
  **5-day incumbent-only concentration cell (#16)**. The sub-forth dip rate is demoted at #15, not
  retired.
