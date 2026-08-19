# 1f916 weather · 2026-08-18 (issue #6)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: full pull at 2026-08-19 02:53 UTC (last in-scope item 08-18 23:44:28), hard cutoff
**2026-08-19 00:00 UTC**. In scope: **12,501 items** (≥ 20 chars), 524 authors, Aug 5 → Aug 18
(complete, 2.9 hours of margin). Issue window (since issue #5's **pull**, 08-18 04:31): **531
items** inside one calendar day — one-day in kind like issue #4's, but covering only the last 70%
of its day where #4's covered 97%. Three instrument changes, all of them consequential: the permeability control
gained a membership decomposition, which **retired the series it was built to defend**; the GPU
stage gained a label-coverage audit, which **found a retro-movement channel** in already-published
numbers; and a new per-issue dip-rate cell shows the pooled statistic issue #4 introduced was
**understating the current rate by nearly half**.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow falling from 224/day at founding to single digits and staying there; register flat well below the human band floor; daily venue share declining out of its prior band and holding two days below the lemmy.world platform line.](figure.png)

## Readings

**Allocation — a second day outside the band; direction not decidable.** The series ran 0.4865
(08-15) → 0.4720 (08-16) → 0.4484 (08-17) → **0.4508** (08-18). The last point is the second
consecutive day below the 0.456–0.548 band that held for nine days through issue #4, so the
excursion issue #5 named is not a one-day artefact. It is also **not a continued decline**: 08-18
is 0.0024 *above* 08-17. Four points, one of them a reversal, on a series this autocorrelated
support neither "still falling" nor "bottomed out" — the decidable statement is that the level has
now sat outside its prior band for two days running.

Against the Usenet anchors' Qwen band (0.085–0.221) the day reads 2.0–5.3× high. Against
**lemmy.world's founding month — a human *platform* that also had to run itself, 0.4665 on the
identical classifier and prompt ([`lemmy_baseline`](../../lemmy_baseline/report.md))** — 08-18
reads **0.966**, the second straight day below the human platform line, after 0.961 on 08-17.
Read against the interval rather than the point (0.4665 [0.4515, 0.4853] author-clustered), both
days also fall clear of the **lower bound** 0.4515: 0.4484 and 0.4508. Issue #5 set three
consecutive such days as the threshold for calling it a sustained period of below-human
self-allocation; **two of the three are in hand**. Over the full 13 days, 10 sit above the platform
point estimate and 3 below.

**Level caveat unchanged**: the absolute number carries the allocation study's 0.31–0.71
specification range; the lemmy comparison holds classifier and prompt fixed on both sides but
inherits that range. The comparator's own bias runs one way — its frame is 55.7% meta-tier, which
makes the human benchmark *more* self-referential and so biases toward the square looking
unremarkable.

**A published number moved, and the mechanism was not in any instrument.** Issue #5 published
08-16 at 0.4726; this issue's pipeline emits **0.4720** for the same day. Nothing about 08-16
changed in the corpus — the feed-lag block finds 0 backfilled items and 0 edits across 11,970
items compared. The cause is the classifier cache: a label is written only when the model answers
VENUE or WORLD, and an unparseable answer caches *nothing*, so that item is silently retried on
the next issue. One such retry succeeded on 08-16, and the move is attributable to the item:
`analysis/weather_label_move.py` searches the integer pairs consistent with both shares and finds
one solution each, **371/785 → 371/786** — so exactly one item gained a label and it was **WORLD**.
That is −0.0006 on a cell that was supposed to be settled. (The tool reports AMBIGUOUS rather than
guessing when more than one pair fits.)

The size is trivial and the direction is arbitrary; the point is that the channel existed
unwatched. The feed-lag block was built to catch exactly this class of problem and cannot see it,
because it hashes *item text* and this is *label coverage*. `weather_gpu.py` now audits it every
issue: per-day coverage, retry counts, and an automatic diff of the emitted series against the
previous published issue. Current coverage is **12,429 / 12,501 (99.4%)**.

The accounting for this issue, which takes some care: the delta pass classified **825** items —
759 new 08-18 items plus **66 retries** of previously-unlabelled ones — and **exactly one retry
resolved** (the 08-16 item above). That leaves **65** persistent failures on already-published
days, joined by **7** first-attempt failures on 08-18, for the **72** items now uncovered. So the
published-day backlog shrank by one, 66 → 65; it did not hold flat. The `label_audit` block in
this issue's `results.json` was emitted by a later verification pass over warm caches and its
`delta_classified: 72` therefore describes *that* pass, not the issue — `weather_gpu.py` now
stamps every audit with a `pass_type` saying which, so the distinction cannot be lost again.

**Structure — inflow did not fall further; no floor established.** New authors per day: 6
(issue #5) → **8**. Newcomer item-share: 0.038 → **0.055**. Issue #5's triggers for "the community
has stopped recruiting" were a zero-author day or a share below 0.03; **neither fired**. Neither
reading is evidence of a floor: 8 sits inside the 6–11 band the series has occupied since 08-14,
and on counts this small the noise is about ±2.5 authors. One day does not undo four: 8/day sits inside the collapsed regime that
began around 08-14, and daily item volume is down 24% over five days (994 → 934 → 794 → 797 → **759**), though not
monotonically.

The published day-window cells moved as they always do — core_n 206 → 210, dominance 88.2 → 88.8,
stability 1.26 → 1.24, permeability 42.9 → 43.9 — and still carry the expanding-span confound, so
they are reported and not read. Under the fixed-observation-span control:

| fixed 7-day span | #1 | #2 | #3 | #4 | #5 | **#6** |
|---|---|---|---|---|---|---|
| core dominance % | 75.8 | 79.2 | 83.0 | 85.8 | 91.3 | **91.8** |
| stability ratio | 1.62 | 1.50 | 1.42 | 1.34 | 1.24 | **1.25** |

**The controlled dominance climb did not repeat issue #5's step.** Issue #5 added 5.5 points at
the 7-day span; this issue adds **0.5**, and **0.8** at the 5-day span (87.6 → **88.4**). Both are
far short of the ≥ 3.7 issue #5 named as the step that would carry dominance above 95%. Whether
that is *deceleration* depends on which width you read: per elapsed day the 7-day series has slowed
for three issues running (2.8 → 1.8 → **0.5**/day) while the 5-day series has not (2.1 → 0.4 →
**0.8**/day). The level is still rising at both widths; the rate is **not decidable**, and this
issue does not claim it. **Controlled stability posted its first non-decline**: 1.24 → 1.25 at the
7-day span, flat at 1.32 over 5 days. After four consecutive falls that is a break in the series,
but +0.01 on a ratio rounded to two decimals is the absence of a further fall, not a reversal. The controlled *permeability* rows disagree across widths this issue
(7-day 46.9 → 43.7, 5-day 46.1 → 47.3) and are not read.

**Permeability — resolved, by retiring the instrument.** Issue #5 carried this forward asking for
a fixed-cohort view. The window handed one over: the **published day-window average** draws on
**exactly the same ten cohorts** as issue #5's, so its membership is held fixed by accident of the
calendar — and it still rose, 42.9 → 43.9. With membership constant, that movement can only be
observation length: the original confound, demonstrated live.

The fixed-horizon cells have their own per-horizon cohort sets, which are **not** all held fixed:
10 shared at N=3 (none entered), 9 at N=4 (08-15 entered) and 8 at N=5 (08-14 entered). Recomputing
each cell over only its shared cohorts reproduces issue #5 **to the decimal** — N=3 32.2, N=4 35.7,
N=5 36.8 — while the all-cohort cells read 32.2 / **37.6** / **38.3**. The gap at N=4 and N=5 is
exactly the entering cohort; at N=3, where nothing entered, there is no gap at all.

That is not a finding about the community; it is a fact about the statistic, and it generalises.
A cohort's fixed-horizon cell is frozen once its N-day window closes, so a shared cohort's value
**cannot** change between issues — the control now asserts this per cohort at every boundary
(it HOLDS at all three horizons here, and a violation would mean the past moved). It follows that
the issue-over-issue movement of the running mean is **100% composition, by construction**. The
monotone rises reported in issues #4 and #5 were reading which cohorts had entered the average,
not how anyone behaved. **The running mean is retired as a behavioural series**, alongside core_n.

The object that does carry behaviour is the per-cohort sequence itself. At N=3, by arrival day:
25.4% (n=224), 23.4 (64), 26.1 (46), 30.4 (56), 33.3 (33), 31.2 (16), 40.0 (20), 17.6 (17), 40.0
(10), 54.5 (11). An author-level permutation test on "do later cohorts convert better?" gives
**r = +0.091, p = 0.044** at N=3, +0.067 (p = 0.137) at N=4 and +0.048 (p = 0.290) at N=5 — three
correlated horizons of one hypothesis, only the shortest nominally significant, no multiplicity
correction, and the correlation is leveraged by a single 224-author cohort against late cohorts of
ten to seventeen. **Direction positive, effect not established.** That is a weaker claim than
either of the last two issues made, and it is the one the data supports.

**Placement — full-pool cells still narrowing, window cells widened, no trigger fired.** Full-pool
bge: lisp **1.230** (1.233), sci **0.657** (0.661), hn **0.610** (0.612); the same direction under
mpnet (lisp 1.253 vs 1.262) and gte (lisp 1.061 vs 1.063). The window cells go the other way, and
against the right comparator — issue #4's one-day window, m=774 — this issue's (m=424) reads
**wider**: bge lisp 1.200 (1.185), sci 0.675 (0.637), hn 0.625 (0.594); gte lisp 1.051 (1.044).
Issue #3's upgrade trigger needed a third consecutive window decline or a gte window cell below
1.0; the bge window series is 1.229 → 1.163 → 1.185 → 1.150 (a *three-day* cell) → **1.200** and
gte stays above parity, so **neither condition fired**. That series mixes window kinds at #5, which
does not matter while no trigger is close but will if one is ever decided on it; issue #7 should
read the trigger on like-kind windows only.

Two separate things make this window thin, and only one is the community. Volume fell 994 → 759
across the five days; the rest of the 968 → 531 shrink is **truncation**, because issue #5's pull
ran at 08-18 04:32 and the window starts there. The **228** in-scope items of 08-18 00:00–04:31 sit
between issue #5's cutoff and this issue's window start, so they enter every full-pool cell and
**no issue's window cells, ever**. Their diurnal position differs from the rest of the day, so the
window-only placement cells are not a random sample of 08-18 either.

**Idea series — the "record low" is an accumulation artefact, and the issue-local cells do not
corroborate it.** Rolling claim-Vendi/W halves read 0.1350 → **0.1295** within this issue (issue #5:
0.1351 → 0.1298), so the cross-issue second-half series is #2 0.1343 → #3 0.1323 → #4 0.1324 →
#5 0.1298 → **#6 0.1295**, a new record low by 0.0003 (the pull-1 figure often quoted alongside
these, 0.1348, is a whole-series mean and does not belong in the second-half sequence). That statistic splits the *whole* series, so
two consecutive issues' second halves cover overlapping but different window sets and the number
lags whatever is happening now — the same defect this issue found in the permeability running mean,
in a milder form. It is demoted rather than retired, because unlike a frozen-cell running mean it
does move with new windows.

The issue-local cells do not corroborate it. Over only the **19 windows this issue added**, the
mean is **0.1299** against issue #5's 63 new windows at 0.1276 — nominally higher, but with a
window standard deviation near 0.006 that difference is **not distinguishable**, by the same
standard applied to the dip counts below. And the sub-forth dip share,
quoted pooled in issue #4 (15.8%) and carried forward by issue #5 without a pooled number, is a
composition statistic too: per issue, over each issue's own new windows, it runs 10.3 → 15.6 →
30.8 → 32.0 → **47.6 → 42.1%**. Against the **23.9%** the pooled cell would report for this issue,
that is the reading the pooled form obscured: windows dip below the nearest anchor roughly twice
as often now as pooling over all history suggests. #6 against #5 is 8/19 against 30/63 — not a distinguishable change, so the
level is high and its direction between these two issues is not decidable. All of this rests on the
shared prefix of consecutive series being bit-identical, which `analysis/weather_dip_rate.py` now
asserts at every boundary; there is **no drift at any boundary to date**.

Issue #5's watch item asked for "a third consecutive decline"; the phrase is ambiguous between the
second-half series (in which #3 → #4 was a rise, so this is the second decline) and the pull-1 →
#4 → #5 sequence (in which it is the third). Rather than pick the reading that fires, both are
recorded and the trigger is **restated for issue #7 unambiguously**: a corridor exit is a
half-window mean below forth's 0.1269. At 0.1295 the series sits 2% above that line, inside the
forth-to-sci corridor where it has been every issue.

**Register — flat.** Daily raw zstd for the new day: **0.6481** (08-17: 0.6445), against a 0.704
human band floor it has never approached. No excursion, no record low.

**Newcomer cells — none, for the first time.** The window carries **42** newcomer items against
489 incumbent, below both standing floors (m ≥ 100 for the Vendi parity/union cells, m ≥ 50 for the
matched NN cell). Nothing is claimed about newcomer refresh in either direction. This is a
consequence of the two readings above meeting: recruitment at ~8 authors/day and a one-day window
no longer produce enough newcomer text to run the instrument at all. At the current level the cell
is only measurable on multi-issue windows, which is a statement about the community, not a gap in
the pipeline.

## Issue #5's watch items, answered by name

1. **Is the excursion a level shift?** — **not yet, and direction not decidable.** 08-18 at 0.4508
   is the first of the two further sub-0.456 days issue #5 required, and it is not a return inside
   the band. The +0.0024 move off 08-17 is well inside this series' daily scatter and says nothing
   about whether the fall has ended. On the lemmy interval: 0.4484 and 0.4508 are two consecutive days below the 0.4515
   lower bound, of the three that issue #5 set.
2. **Does inflow floor or keep falling?** — **did not fall further; floor not established.** 6 → 8
   new authors, share 0.038 → 0.055; neither the zero-author nor the sub-0.03 trigger fired. 8 is
   inside the 6–11 band held since 08-14, so this is one point in the existing scatter.
3. **Dominance under control.** — **the step did not repeat**: +0.5 points at the 7-day span and
   +0.8 at the 5-day, against the ≥ 3.7 that would have approached 95%. Per elapsed day the two
   widths disagree about whether the climb is slowing, so no rate claim is made. Controlled
   stability posted its first non-decline (1.24 → 1.25).
4. **Window comparability.** — this issue's window is **one day, 531 items**. Window cells are
   compared to issue #4's one-day window (968 items) throughout, never to issue #5's three-day one,
   and the item counts are stated because #6's window is 55% the size of #4's.
5. **Idea-series second half.** — **0.1295, a new record low by 0.0003**, still above forth — but
   the cell is an accumulation statistic and the issue-local mean went the other way (0.1276 → 
   **0.1299** over each issue's own new windows). The trigger as worded was ambiguous; both readings
   are reported and the replacement trigger is a half-window mean below 0.1269.
6. **Permeability under control** (carried from issue #4 via #5) — **resolved**: the running mean
   is a composition statistic by construction and is retired; the per-cohort trend is positive but
   not established (r = +0.091, p = 0.044 at N=3 only).

## Watch items for issue #7

1. **The allocation excursion needs one more day.** One further day at or below 0.456 makes it a
   level shift by issue #5's rule; a day back inside the band makes 08-17/08-18 a two-day dip. On
   the human comparator, one more day below **0.4515** completes the three-day threshold for a
   sustained period of below-platform self-allocation — the first such finding if it lands.
2. **Is the inflow floor real?** 8/day is one day above the record low. Two more days at or above
   8, or a newcomer item-share above 0.076, would say the collapse has bottomed; a return to 6 or
   below says 08-18 was noise.
3. **Controlled dominance and stability.** Dominance at 91.8% and stability at 1.25 both moved by
   ≤ 0.5 this issue, and the 7-day and 5-day widths disagree on the per-day rate. A second
   consecutive near-flat issue **at both widths** is the point at which "core concentration is
   rising" stops being the reading and "it has plateaued near 92%" starts; disagreement between
   widths again means neither reading is available.
4. **The newcomer instrument is dark.** This is the first issue it has been skipped entirely. If
   issue #7's window also falls below m = 50 newcomer items, the per-issue cell should be replaced
   by a pooled window spanning the last three issues rather than reported as skipped twice.
5. **Label coverage.** 72 items have never produced a parseable classifier answer; 65 of them were
   in scope for issue #5 too, so they have now failed in two consecutive issues. If that count grows rather than converges, the classifier prompt — not the cache —
   is the problem, and a fallback parse (or an explicit UNKNOWN class carried into the denominator)
   is needed. Either way the audit reports any published day that moves.
6. **Dip rate, now that it is measured per issue.** 47.6% then 42.1% of new windows below forth,
   on 63 and 19 windows. A third issue in the 40s makes "roughly half of all windows now dip below
   the nearest anchor" a standing reading; a drop into the 20s–30s would make #5 the outlier.
7. **Per-cohort conversion, with the horizons pre-registered.** N=3 is the only horizon that
   reaches nominal significance and it is the one with the most cohorts; issue #7 should read N=3
   as the primary and the others as supporting, rather than three co-equal tests.

## Method notes & caveats

- **Cutoff** 2026-08-19 00:00 UTC, exclusive; the pull ran 2.9 h after it and the last in-scope
  item is 08-18 23:44:28, so no in-scope day is partial. 08-18 cells are labelled provisional as
  standing discipline.
- **One-day window** (531 items, 08-18 04:31 → 23:44). Window-only cells are comparable in kind to
  issue #4's one-day window and not to issue #5's three-day one; at 55% of #4's item count they
  carry wider bands. The full-pool column is where the narrowing should be read.
- **No newcomer cells**: 42 newcomer items against floors of m ≥ 100 (Vendi) and m ≥ 50 (NN).
- **Delta pipeline.** Claims and allocation labels are cached by `kind:id`; 759 items claimified
  this issue, 0 cache evictions for edits (0 edited items across 11,970 compared). Frozen anchors
  are never re-measured, and their hashes are unchanged.
- **Allocation labels retro-move.** Unparseable classifier answers cache nothing and are retried,
  so a published day can shift when a retry succeeds; 08-16 moved −0.0006 this issue. Audited every
  issue from here in `allocation_trend.label_audit`, including an automatic diff against the
  previous published issue.
- **Single-normalizer / bge-only cells.** The rolling series and newcomer cells are Qwen-normalized
  and bge-embedded only; the three-embedder check is run for placement alone.
- **Allocation currency.** Venue share is the Qwen binary classifier. The LEVEL carries the
  allocation study's 0.31–0.71 specification range; κ(Qwen, Gemma) is 0.428 on this pool. The TREND
  is the cleaner object.
- **The lemmy reference is frozen.** lemmy.world's founding month is a fixed 2023 corpus read from
  `results/lemmy_baseline/results.json` by `analysis/weather_lemmy_ref.py`; it is not re-measured
  per issue. Its platform share is a point estimate with a band, 0.4665 [0.4515, 0.4853].
- **Accumulation statistics.** Three cells in this report average over history that grows each
  issue: the rolling halves, the pooled dip share, and (until this issue) the fixed-horizon
  permeability mean. Where an issue-local equivalent exists it is now the primary reading and the
  pooled form is kept for continuity. The validity of every per-issue decomposition here rests on
  the shared prefix not moving, which is asserted rather than assumed.
- **Retired series.** core_n (issue #5) and, from this issue, the fixed-horizon permeability
  running mean. Both were reading construction rather than behaviour. The fixed-span churn control
  still carries an uncontrolled membership term.
- **The per-cohort trend test** is three correlated horizons of one hypothesis with no multiplicity
  correction; read as direction, not as an established effect.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators; concentration readings are about identities.
