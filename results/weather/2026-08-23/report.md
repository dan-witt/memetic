# 1f916 weather · 2026-08-23 (issue #11)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-24 01:21 UTC (last in-scope item 08-23 23:59:48), hard
cutoff **2026-08-24 00:00 UTC**. In scope: **19,334 items** (≥ 20 chars), 933 authors, Aug 5 → Aug
23 (complete, 1.35 hours of margin). Issue window: **2,169 items, all of 08-23** — the second pair
of exact-calendar-day windows, and the first pair whose placement band widths are comparable. One
fact organises the issue: **the recruitment event's third day separated two things that moved
together on 08-22**. Arrivals fell from 258 to **70** while volume held at **2,169**, 91% of the
record — **128 of the 258** who arrived on 08-22 came back and posted 932 items, 43% of the day,
and that is what carries the traffic.
Against that, the allocation cell delivers a result issue #10 could not: **issue #8's
pre-registered condition holds for a third consecutive issue, and this time the day that completed
it argues the same way.** Issue #10 pre-registered the exact bar — the trailing 5-day mean stays
below 0.4515 if and only if 08-23 reads below 0.4591 — and 08-23 read **0.4416**, clearing it by
0.0175. The crossing **deepened** from 0.23 to **0.50** counting standard errors, and 08-23's own
share sits below the bound (−0.93 SE) and below the lemmy.world platform point (**−2.33 SE**),
where issue #10's completing day sat at −0.12 SE and read as nothing at all. One instrument
introduced at issue #10 to temper its own conclusion now cuts the other way — the compositional
decomposition has nothing to explain away on a day that fell — and the other is **withdrawn as
ill-posed**: the published/incumbent gap is identically newcomer-weight × difference, and its
collapse from 0.0224 to 0.0060 is the weight falling 3.4× while the difference held. And the **n ≥ 10 per-cohort conversion
cell unfroze** after five bit-identical issues, exactly on the schedule issue #10 published, with
08-21's 71-author cohort entering at **18.3%** — the lowest of any cohort with fifty or more
members. Separately, this issue is the first to run the feed-lag instruments as queries over the
observation store, and that change shipped with defects: one found in production and four more by
the cold review, including a timestamp-resolution bug that stopped this issue re-deriving itself
and had already moved a published control. All are fixed, and both issues now reproduce 14/14.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor with no visible break; author inflow showing the three-day event as 71, 258 then 70 against a founding day of 224; register drifting slightly upward in mid-band and nowhere near the human floor; daily venue share falling from the 08-22 rebound to 0.4416, clearly below the lemmy.world platform line, under both parses.](figure.png)

## Readings

**Allocation — the pre-registered condition holds for a third issue, and this time nothing has to
be taken back.** The daily series ran 0.4367 (08-19) → 0.4699 → 0.4265 → 0.4653 (08-22) →
**0.4416** (08-23). The trailing 5-day mean reads 0.4465 (08-21) → 0.4498 (08-22) → **0.4480**
(08-23), against the bound of 0.4515.

Issue #10 did something this series had not done before: it published the **exact threshold** the
next issue would have to clear. The trailing window for issue #11 is 08-19…08-23, whose first four
days sum to 1.7984, so the mean stays below 0.4515 if and only if 08-23 reads below **0.4591**.
08-23 read **0.4416** and cleared the bar by 0.0175. That is a pre-registration in the strong
sense — the number was fixed and published before the day existed — and it is met.

Three things follow, and unlike issue #10 all three run the same way:

- **The crossing deepened.** 0.4515 − 0.4480 = **0.0035**, against a binomial counting standard
  error of **0.00695** for a five-day mean over these days' labelled counts — **0.50 SE**, against
  0.23 SE at issue #10 and 0.62 SE at issue #9. The run below the bound is now three consecutive
  days (08-21, 08-22, 08-23).
- **The day that completed it argues the same way.** 08-23's own share is 0.0099 below the bound,
  which is **0.93 SE** on the day's own counting error of 0.0107. Issue #10 had to publish the
  opposite: its completing day rose to 0.4653 and sat *above* the bound.
- **The daily direction remains not decidable.** Three of the last five daily moves are negative
  (p = 0.50 against fair-coin signs). The clustering permutation reads **p = 0.1716** over 18 days
  with 5 below the bound and the longest run still 3 — *weaker* than issue #10's 0.0824, because
  08-23 adds a fifth below-bound day that does not extend the run.

**None of this makes the level a settled reading, and the reason is unchanged: the depth is half a
standard error.** A rule satisfied three times at 0.62, 0.23 and 0.50 SE is a rule whose statistic
has never been more than two thirds of its own noise away from the bound. What has changed since
issue #10 is that the tempering instruments no longer temper: the compositional decomposition that
explained away 08-22's rise finds nothing to explain this issue, and the incumbent-only series that
was introduced to separate level from composition has converged back onto the published one.

**Against the human platform, 08-23 is a reading, and a substantial one.** The day reads 0.4416
against [lemmy.world](../../lemmy_baseline/report.md)'s **0.4665** platform point: a gap of −0.0249
on a day whose own binomial counting standard error is **0.0107**, i.e. **−2.33 SE**. That is the
same magnitude as 08-21's −2.33 SE and far outside issue #10's −0.12 SE. Eleven of eighteen
classified days sit above the platform figure and seven below, under both parses. The comparator's
own interval ([0.4515, 0.4853]) is wider still, and none of this includes classifier error.

**The incumbent-only allocation series converged back, which is the branch issue #10 named.**
Issue #10's watch item #2 set them: *"If incumbents stay near 0.44 while the published series is
dragged around by arrivals, the incumbent-only cell is the level and should be said so; if it
converges back, this issue's separation was the arrival event and nothing more."*

| | 08-17 | 08-18 | 08-19 | 08-20 | 08-21 | 08-22 | **08-23** |
|---|---|---|---|---|---|---|---|
| published daily share | 0.4484 | 0.4508 | 0.4367 | 0.4699 | 0.4265 | 0.4653 | **0.4416** |
| incumbents only | 0.4516 | 0.4416 | 0.4353 | 0.4674 | 0.4256 | 0.4429 | **0.4356** |
| gap | −0.0032 | 0.0092 | 0.0014 | 0.0025 | 0.0009 | **0.0224** | **0.0060** |

**The gap did collapse — 0.0224 to 0.0060 — but the branch it was supposed to decide was
ill-posed, and this issue withdraws it.** The gap between the published and incumbent-only series
is not an independent quantity. Identically,

> day share − incumbent share = **newcomer weight × (newcomer share − incumbent share)**

and the identity holds to four decimals on all eighteen days
(`analysis/weather_alloc_by_cohort.py`, `gap_identity_check`). Across the two days in question:

| | newcomer weight | difference | gap |
|---|---|---|---|
| 08-22 | 0.6144 | +0.0365 | **0.0224** |
| 08-23 | 0.1798 | +0.0335 | **0.0060** |

**The difference barely moved; the weight fell 3.4×.** So the gap was always going to collapse once
arrivals fell, whatever newcomers did, and its collapse is not evidence that "the separation was the
arrival event *and nothing more*". Issue #10 asked the wrong question of this cell: it framed a
branch on the gap, which is a product, when only one of the two factors carries information about
behaviour.

**The factor that does carry it is the difference, and it is stable.** On the only two days with
enough newcomers to measure it at all, newcomers allocate **+0.0365** (08-22, n = 1,450) and
**+0.0335** (08-23, n = 388) more venue-ward than incumbents — permutation p = 0.0922 and 0.2395,
neither significant alone, but running the same way and at the same size. Every other day's
difference rests on newcomer counts between 7 and 319 and swings from −0.0849 to +0.2468, which is
noise. So the supported statement is that **newcomers have allocated ~3.4 points more venue-ward
than incumbents on both days that could resolve it**, and that this difference, not the gap, is
what issue #12 should track. If arrivals return, the gap re-opens mechanically.

The incumbent point itself reads 0.4356 on 1,770 labelled items (counting SE 0.0118), against
0.4429 on 08-22; the incumbent-only trailing 5-day mean is **0.4414**. Composition accounts for
0.0060 of the day's level, and the day **fell**, so no compositional story is needed to explain a
rise this issue — which is the job issue #10's cell was built for.

**Label coverage — stable, still one-sided, for a sixth consecutive issue, with one new wrinkle.**
The uncovered count went 113 → **124**: the same 113 plus 11 on 08-23, a failure rate of 0.51%
(11/2,169) against 08-22's 0.84%, the best of the last four days. Coverage is 19,210/19,334
(**99.4%**). **122** of the 124 return the verbatim string `SUBJECT MATTER`, so the failure remains
one-sided and the strict series remains an upper bound on venue share. Two items resolved on
retry — the first nonzero count in the series — and `weather_label_failures.py`'s own note
attributes a nonzero retry count to batch-composition nondeterminism rather than new information,
so it is reported and not read. The corrected parse moves 08-23 from 0.4416 to **0.4394**, and both
series are published with the strict one remaining the cross-issue currency.

**Structure — the event's third day, and the first day that separates arrivals from traffic.**

| | 08-19 | 08-20 | 08-21 | 08-22 | **08-23** |
|---|---|---|---|---|---|
| new authors | 5 | 5 | 71 | 258 | **70** |
| active authors | 121 | 118 | 177 | 393 | **317** |
| items | 746 | 702 | 836 | 2,380 | **2,169** |
| newcomer item share | 0.012 | 0.010 | 0.238 | 0.613 | **0.179** |

**Arrivals fell 3.7× while volume held at 91% of the record.** That is the fact issue #10 said two
days could not deliver: 08-21 and 08-22 could not tell a step from a spike, and 08-23 answers a
narrower question than either — *the arrival rate fell sharply and the traffic did not*. The
mechanism is visible in the newcomer item share: 0.613 → 0.179 means 08-23's volume is being
carried by authors who were not newcomers, i.e. by the 258 who arrived the day before. Two limits
on how far that goes. Seventy arrivals is **fourteen times** the 5/day that ran on 08-19 and 08-20,
so the recruitment has not stopped, only fallen; and one day of retention is not retention.

**The published day-window cells now move in a way that is finally legible.** core_n 230 → **244**
(up 14), dominance 81.8 → **77.7**, stability 1.25 → **1.26**, permeability 48.3 → **45.6**. The
permeability cell is worth naming: across the nine issues that published it (#2–#10) it rose monotonically, 33.6 → 35.5 → 39.4 →
42.9 → 43.9 → 46.9 → 47.2 → 48.2 → 48.3, and this is its **first fall**. That is not read as a
change in the square — these cells carry the expanding-span confound and 08-22's 258 authors are
now eligible for core membership on a second day — but the direction change is recorded.

**Concentration — the control got its real test, and passed it across two issues.** Under the
fixed-observation-span control:

| fixed span, 5-day | #7 | #8 | #9 | #10 | **#11** |
|---|---|---|---|---|---|
| uncontrolled dominance % | 91.0 | 93.2 | 89.1 | 61.4 | **52.1** |
| incumbents only | 93.6 | 93.6 | 94.3 | 93.2 | **93.3** |

| fixed span, 7-day | #7 | #8 | #9 | #10 | **#11** |
|---|---|---|---|---|---|
| uncontrolled dominance % | 91.7 | 93.8 | 92.2 | 70.7 | **61.3** |
| incumbents only | 95.0 | 94.5 | 95.9 | 96.3 | **95.8** |

**Over two issues the uncontrolled 5-day cell fell 89.1 → 52.1, thirty-seven points, while the
incumbent-only row moved 94.3 → 93.3, one point.** Issue #10 demonstrated this on a single day and
said so; it now holds across two, including a day on which arrivals collapsed and the uncontrolled
cell **kept falling** — because the five-day span still contains 08-22. That is the clearest
statement the series has of what the uncontrolled cell measures: not concentration, but how many
people arrived inside the window.

Issue #10's watch item #3 asked for the other half of the validation: *"a control that never moves
is not a control. Issue #11 should say what would move it."* The honest answer is that this issue
could not run that test — 70 arrivals is a smaller influx, not an absent one — so the pre-registration
is owed to issue #12 and is written into the watch items below.

**Per-cohort conversion — the n ≥ 10 cell unfroze, on schedule, and the entering cohort converts
low.** Issue #10 wrote that 08-21's 71-author cohort would enter the N=3 table at issue #11 after
five bit-identical issues. It did.

| horizon (n ≥ 10 floor) | cohorts | authors | cell | (issue #10) |
|---|---|---|---|---|
| **N=3 (primary)** | 11 | 568 | **30.9** | 32.2 (5 issues bit-identical) |
| N=4 | 10 | 497 | 37.6 | 37.6 |
| N=5 | 10 | 497 | 41.7 | 41.7 |

The entering cohort — 08-21, n = 71 — converts at **18.3%**. Three disciplines go with that number.
The cell is an **unweighted mean over cohorts**, so the entering cohort moves it by
(18.3 − 32.2)/11 = **−1.26 points**, which is the whole move; per-cohort identity across the
boundary **HOLDS** at all three horizons, so nothing else drifted. N=4 and N=5 are unchanged
because 08-21 does not enter those until issues #13 and #14. And **one cohort is not a trend**:
18.3% is the lowest of the four cohorts with n ≥ 50 (08-06 25.4%, 08-07 23.4%, 08-09 30.4%), and
against the author-weighted mean of all prior n ≥ 10 cohorts (27.7%, n = 497) it is 9.4 points low,
about **1.9 counting SE** — suggestive, not resolved, and it arrived inside a recruitment event.
The retired n ≥ 5 cell was **not** resurrected to read this, per issue #10's instruction.

The fixed-horizon permeability control moves for the first time in five issues for the same reason:
N=3 32.2 → **30.9**, with N=4 (37.6) and N=5 (41.7) unchanged.

**Newcomer — the precision branch fired, exactly as issue #10 pre-registered.** The window carries
**389 newcomer items against 1,780 incumbent**, against issue #10's 1,458/922.

| per-issue window cell | issue #11 | issue #10 |
|---|---|---|
| within-pool parity | **1.011** [0.978, 1.044] | 1.030 [1.009, 1.052] |
| union over incumbent | **1.017** [0.997, 1.046] | 1.027 [1.008, 1.042] |
| nearest-incumbent distance, matched pools | Δ **0.0077** [0.0026, 0.0126], p = **0.04** | Δ 0.0114 [0.0051, 0.0184], p = 0.008 |

Issue #10's watch item #6 set the branches: *"If a smaller window returns bands that span 1 at a
similar point estimate, the reading was precision; if the point estimate falls too, something about
newcomers changed with the event."* **Both Vendi bands went back to spanning 1** when *m* fell 3.7×,
and the bands widened by about half. But the point estimates **also fell** (1.030 → 1.011,
1.027 → 1.017), so the branches are not cleanly separated. The disciplined statement is the mutual
one: **each issue's point estimate sits inside the other issue's band**, so no change in the
underlying quantity is detectable, and a modest true fall cannot be excluded either. The cells
simply cannot resolve a ~2% move at this window size.

The nearest-incumbent finding is the stable one: newcomer claims sit measurably farther from the
incumbent cloud than incumbents sit from each other, for a **fifth** consecutive issue — though
weaker this issue (Δ 0.0077 at p = 0.04 against 0.0114 at p = 0.008). The pooled cell agrees at
larger scale (3,277 newcomer / 2,108 incumbent over 3.0 days; parity 1.033 [1.020, 1.047], union
1.026 [1.019, 1.035], Δ 0.0140 [0.0091, 0.0186], p ≈ 0.000) and shares **59.7%** of its items with
issue #10's, so consecutive pooled points remain dependent and are not a two-point trend.

**Placement — full-pool flat for a fifth issue, and the first pair of comparable window bands.**
Full-pool bge: lisp **1.223** (1.228), sci **0.656** (0.657), hn **0.613** (0.609); mpnet lisp
**1.265** (1.265) and gte lisp **1.062** (1.066). Every move sits far inside its own band (bge full
lisp [1.193, 1.257]).

| window-only | #9 (836 items) | #10 (2,380) | **#11 (2,169)** |
|---|---|---|---|
| bge lisp | 1.192 | 1.192 | **1.207** |
| mpnet lisp | 1.215 | 1.203 | **1.216** |
| gte lisp | 1.051 | 1.058 | **1.050** |

Issue #10's watch item #5 asked whether the window would again hit the m = 1500 draw cap, because
band widths are only comparable between windows that both do. **It did** — so #10 and #11 are the
first pair whose window band widths are comparable, where #9's 836-item window gave only m = 668.

**Issue #3's upgrade trigger does not fire, and its decline arm has reset.** The gte arm — *any gte
window cell < 1.0* — reads **1.050** and is live every issue. The decline arm needs three
consecutive declines in the bge window series; #9 → #10 was flat (1.192 → 1.192) and #10 → #11 is a
**rise** (1.192 → 1.207), so **zero declines are banked** and that arm cannot complete before
**issue #14**. Issue #10 wrote "cannot complete before issue #13" on the basis of one flat
transition; the rise pushes it out by one more.

**Idea series — the dip rate came back down, which is the fourth reversal in six issues.** Over the
**54 windows this issue added** the sub-forth dip rate is **16.7%** (9/54), against 26.7% (16/60) at
issue #10 — Fisher two-sided p = **0.2582**, which on threefold-overlapping windows is
anti-conservative and therefore not a finding. Over seven issues the cell has read 47.6, 42.1, 10.5,
11.8, 4.8, 26.7, **16.7**. Issue #10's summary stands verbatim and this issue supplies a seventh
point for it: **this cell's issue-to-issue range spans 5% to 48% with no ordering that survives**,
and no reading should be built on it at this window count.

The new-window mean is 0.1320 (0.1297). The pooled share fell 22.2 → 21.6%, which is composition.
**The shared-prefix assertion passed for a fourth consecutive issue** — 0 of the 427 shared windows
moved, as required by 0 edited items over 17,335 compared.

Rolling halves read 0.1334 → **0.1305** (issue #10: 0.1340 → 0.1298), so the cross-issue second-half
series is #5 0.1298 → #6 0.1295 → #7 0.1295 → #8 0.1297 → #9 0.1300 → #10 0.1298 → **#11 0.1305**,
an accumulation statistic reported for continuity and not read. At 0.1305 the series sits 2.8%
above forth's **0.1269**, inside the forth-to-sci corridor where it has been every issue.

**Register — the second-highest day of the series, and still nowhere near the floor.** Daily raw
zstd: 0.6470 (08-21) → 0.6496 (08-22) → **0.6539** (08-23). That is the series'
second-highest value behind 08-20's 0.6571. The eighteen-day series (08-05 falls below the 50-item
floor) spans 0.6367–0.6571 and sits **0.050 below the 0.704 human band floor** measured from the
newest day; measured from the series high the gap is 0.047, and the two sentences are not
interchangeable. Issue #10's watch item #7 asked this cell to say what magnitude of event would be
expected to move it, and this issue owes an answer rather than another observation — see the watch
items. No previously published register figure is revised, because no item was edited.

**Feed lag — three backfilled items, and the first issue whose window holds more than one
observation.** The block finds **3** items on 08-23 that the previous issue's pull missed, aged
0.05 h median and 0.13 h at p90, revealing **1** new author. Derived across issues #3–#11 the
backfill record is 0, 1, 3, 0, 1, 0, 2, 7, **3**. The pull margin was **1.35 h** against issue
#10's 0.87 and issue #8's 23.71. The standing shape of the record holds: **every backfilled item so
far has been minutes old at the missed pull**, which is a pull-boundary race rather than a lagging
feed. Trailing-day numbers stay provisional.

**Zero edited items, over 17,335 items compared, at 100% audit coverage.** That last number is new
and is the point of the instrument change: the audit no longer rests on an assumed full re-read but
on how much of the corpus was actually re-verified since the previous issue. Every thread and every
item qualifies this issue, because a full pull ran at 08-23 17:12 in the course of the tooling work.
Future issues running catch-up only will have audit coverage well below 100%, and must report it.

## The instrument change, and four bugs in it

From this issue the feed-lag cells are **queries over the observation store**
(`analysis/corpus_store.py`), not diffs of two corpus trees. This series' rule is that an instrument
change gets disclosed and its comparability assessed, so:

- **Verified measurement-neutral at the changeover — but that verification had a hole, and the
  cold review found it.** Re-running the whole pipeline at issue #10's parameters reproduced every
  published cell: 14/14 store queries, 25/25 `weather_cpu`, 29/29 `weather_gpu`, 0 mismatches
  across all four controls. What nobody had done was run the verifier against the **new** issue.
  Doing so returned **6/14**. The cause: `corpus_fetch.py` stamped observations with a fractional
  `time.time()`, while an issue's published `pull_at` is formatted to whole seconds — so
  `first_seen_at <= observed_at` dropped the run's own 818 rows and **issue #11 could not
  re-derive itself**. The migration-seeded rows that issue #10 rests on carry whole-second stamps
  by construction, which is exactly why #10 passed throughout and the defect stayed invisible.
  It was live: re-running `weather_churn_control.py` gave issue #11's rows as 53.3/92.4 and
  63.2/95.9 against the published 52.1/93.3 and 61.3/95.8, so issue #12's control tables would
  have printed a wrong #11 row — inside a watch item that pre-registers a 3.0-point trigger band.
  Observation and run stamps are now recorded at the resolution they are published at, the 818
  rows were repaired to their whole second, and **both issues now reproduce 14/14** with the
  controls reproducing their published rows exactly.
- **The change paid out immediately.** Between issue #10's pull and this one there were **two**
  observations in the log — a full pull at 08-23 17:12 and this issue's catch-up at 08-24 01:21.
  (A third run at 17:31 fetched nothing and appended no rows, so it is a run record, not an
  observation.) Under the retired scheme the 17:12 pull would have silently moved this issue's
  feed-lag baseline, because that baseline was `git archive HEAD data/posts` and therefore a
  function of when the corpus was committed. It is now the previous issue's published `pull_at` and
  cannot move.
- **Sensitivity is not reduced by the extra runs.** Every item that could qualify as backfill was
  created at or before 08-23 00:50 and therefore sat inside the 17:12 full re-read of all 1,803
  threads. This issue's 3 is measured on an instrument at least as sensitive as issue #10's 7.
- **The backfill boundary is now a named basis.** `prev_last_item` reproduces the series and is
  what is published; `prev_run` is the stricter reading. They differed by one item at issue #10 and
  by two here (3 against 5).
- **The verifier was measuring the wrong window, and was fixed with the above.** Letting
  `backfill()` fall back to consecutive observation times compares the last two **runs**, which
  stopped being the last two **issues** the moment catch-up runs landed between them: it returned
  5 against the published 3. It now takes the previous issue's published `pull_at` explicitly, as
  `weather_cpu.py` does, and rebuilds the derived index rather than trusting whatever is on disk.

**A bug in the new fetcher was found and fixed in the course of producing this issue, and it was
load-bearing for a number this issue publishes.** `analysis/corpus_fetch.py` built a map of every
thread it had successfully fetched and never wrote it back; `corpus_store.save_thread_state()` and
`load_thread_state()` had no callers anywhere in the repository. Two consequences:

1. `coverage()` reads `threads.last_fetched_at`, which therefore only ever held what the migration
   stamped — 1,803 threads carrying one identical timestamp. This run's 646 genuinely re-verified
   threads did not count, and the figure **decays to 0.0% about 24 hours after the migration no
   matter how much is fetched**. Coverage is precisely the number the store exists to let a report
   state, so "0 edited items" would have rested on an instrument measuring nothing.
2. `stale_threads()` scores by (now − last_fetched)/(now − last_activity), so the sweep re-picked
   the same threads every run and never converged.

Fixed by writing the map back before the index rebuild. Verified offline against a scratch copy of
the store: with stamps aged past the window the old code reports 0.0% coverage, while the fixed
code registers 32.1% after a 600-thread run and those threads leave the sweep queue. For this issue
the 646 threads the run actually wrote were stamped from their real fetch mtimes; the other 1,224
kept the 17:12 pull stamp, because their file mtimes record a git checkout at 19:07 and not a
verification. Published coverage would otherwise have read 96.4%.

**The same review found three more defects of that class in the same file, all now fixed and none
of which had yet fired.** A thread that 404s never updated `last_fetched_at`, so the sweep would
re-pick it forever — a 404 is a verification, since we asked and it is gone. In catch-up mode the
cursor advanced and persisted even when the budget stopped the run before every thread the changes
feed had named, silently dropping those threads; the cursor is now held back and the run marked
incomplete whenever a feed thread goes unfetched. And sorting the union of feed and sweep targets
by thread id could spend the whole budget on sweep targets while feed threads waited, so feed
targets now go first. On an 08-22-scale day — 447 threads touched against a default budget of 400 —
the second and third are reachable rather than theoretical.

## What the influx looks like on its third day

| | 08-21 | 08-22 | **08-23** |
|---|---|---|---|
| new authors | 71 | 258 | **70** |
| hours of the day they arrived in | 9 / 24 | 24 / 24 | **23 / 24** |
| share in the busiest hour | 25% | 8% | **10%** |
| items per author (median / max) | 2 / 21 | 3 / 21 | **4 / 21** |
| items per **active** author | 4.72 | 6.06 | **6.84** |
| threads touched | 246 | 447 | **438** |
| median chars, newcomers vs incumbents | 1,603 / 1,148 | 1,282 / 1,256 | **1,178 / 1,642** |
| distinct platform model labels among arrivals | 36 | 101 | **46** |

**08-23's arrivals look like 08-22's, at a quarter of the scale, and the incumbent side is what
moved.** The 70 arrivals still spread across essentially the whole clock with no hour holding more
than 10%, so the profile does not revert to 08-21's evening burst. What changed is the incumbent
column: median incumbent length rose to 1,642 characters against 1,256 on 08-22, and distinct
incumbent model labels rose 56 → 96 — both of which are the 08-22 cohort being counted as
incumbents for the first time, not a change in anyone's behaviour. Newcomers now write **shorter**
than incumbents (1,178 vs 1,642) where on 08-22 the two were indistinguishable.

**The `max` column is a platform constant and carries no information about the event.** The platform
caps comments at **20 per author per day**, and the cap is hard: across 19 days and 2,987
author-days, **no non-admin author has ever posted a 21st comment**. Posts are not capped the same
way — 1,787 author-days made exactly one and four made between three and six — so the modal
per-author daily maximum is 1 post + 20 comments = **21**, which is the exact composition of 245 of
the 246 author-days sitting at 21. Every one of the six author-days above 21 is either the
platform's own account `1f916-agent` (five of them; exempt, reaching 47 comments and 7 posts in a
day, and 1.60% of the corpus) or a single author who made six posts while still stopping at 20
comments. Earlier issues reported per-day maxima of 44, 25, 41, 49, 47 and 26 without naming the
cause; all six are that admin account and that one six-post day.

**The cap changes what day-volume can mean, which bears directly on this issue's headline.** Past
~21 items per active author a day cannot get bigger except by recruiting, so items-per-active-author
belongs beside the raw count. That series reads 4.94 (08-06), then 5.95–7.65 on every day from 08-07 to 08-20, then
**4.72** (08-21), **6.06** (08-22), **6.84** (08-23). Arrival days depress it
mechanically, because a day full of authors posting once or twice pulls the mean down. So 08-23
held 91% of the record volume on 3.7× fewer arrivals by returning to the intensity the square ran
at *before* the event — not by anyone posting unusually hard. At 6.84 against a ceiling of 21 there
is room for volume to grow without recruitment, so the cap does not yet bind; it only says that a
day much bigger than 08-22's would have to bring more people.

Two limits carried forward from issue #10. This is **descriptive, not a test**. And the model-label
column uses the **platform's own label**; it is not an author clustering, and identity remains
forum identity rather than operator.

## Issue #10's watch items, answered by name

1. **Does 08-23 read below the pre-registered 0.4591?** — **yes, 0.4416**, clearing by 0.0175, so
   the trailing 5-day mean stays below 0.4515 for a third consecutive issue at 0.4480. The crossing
   **deepened**: depth 0.0017 → 0.0035, i.e. 0.23 → 0.50 counting SE. Unlike issue #10 the
   completing day argues the same way, sitting 0.93 SE below the bound and 2.33 SE below the
   platform point.
2. **The incumbent-only allocation series gets its second point.** — **the gap collapsed
   (0.0224 → 0.0060), but the branch is withdrawn as ill-posed.** The gap is identically
   newcomer-weight × difference; the weight fell 3.4× while the difference held (+0.0365 →
   +0.0335), so convergence was guaranteed by the arrival collapse and decides nothing about
   behaviour. The difference is the object, and on the only two days large enough to measure it
   newcomers allocate ~3.4 points more venue-ward than incumbents. Incumbents read 0.4356; the
   incumbent-only trailing mean is 0.4414.
3. **Does the incumbent-only concentration cell stay flat when the influx stops?** — **it stayed
   flat (93.2 → 93.3 at 5 days, 96.3 → 95.8 at 7) but the influx did not stop**, so only half the
   question was askable. What this issue does add is the two-issue version of the demonstration:
   uncontrolled 89.1 → 52.1 against incumbent-only 94.3 → 93.3. The "what would move it"
   pre-registration is owed and is written below.
4. **The n ≥ 10 cohort cell unfreezes.** — **it did, on schedule.** 08-21's 71-author cohort
   entered N=3 at **18.3%**, moving the cell 32.2 → 30.9; per-cohort identity HOLDS at all three
   horizons; N=4 and N=5 are unchanged until issues #13 and #14. The retired n ≥ 5 cell was not
   resurrected.
5. **The second exact-calendar-day window pair, and is it again at the m = 1500 cap?** —
   **delivered, and yes.** #10 and #11 are the first pair with comparable band widths. bge window
   1.192 → 1.207 (a rise), mpnet 1.203 → 1.216, gte 1.058 → 1.050. Issue #3's decline arm now has
   zero declines banked and cannot complete before issue #14.
6. **Do the newcomer Vendi cells fall back to spanning 1 when n drops?** — **yes, both of them**,
   at *m* down 3.7×. But the point estimates fell too, so the branches are not cleanly separated;
   each issue's point sits inside the other's band and no change is detectable either way.
7. **Does anything move register, and what magnitude of event would show up in it?** — **08-23 rose
   to 0.6539**, the series' second-highest, on a day of 2,169 items. The question is answered
   properly in the watch items below rather than deferred a sixth time.
8. **Backfill per thousand items as well as raw count.** — **adopted**: 3 items on 2,169 is
   **1.38 per thousand**, against issue #10's 7 on 2,380 = 2.94 and issue #9's 2 on 836 = 2.39. On
   that scale this issue's count is the *lowest* of the three event days, where the raw counts
   suggested a middling one.

## Watch items for issue #12

1. **The decider's threshold, pre-registered again.** For issue #12 the trailing window is
   08-20…08-24, whose first four days sum to 1.8033, so the mean stays below 0.4515 if and only if
   **08-24 reads below 0.4542**. The bars run 0.4517 (#9), 0.4736 (#10), 0.4591 (#11) and 0.4542
   (#12) — the first two derived retroactively at issue #10, only #11's and #12's pre-registered
   in advance — so issue #12's is **harder than the two issues before it and easier only than
   issue #9's** — a higher bar is easier, since the test is to read below it. A day above 0.4542
   ends the run at three.
2. **What would move the incumbent-only concentration cell.** Pre-registering it now, as issue #10
   asked: the cell has read 91.3, 91.4, 93.6, 93.6, 94.3, 93.2, 93.3 at 5 days across issues
   #5–#11, a range of 3.0 points. **A move of more than 3.0 points in either direction, on a day
   with fewer than 100 arrivals, is a reading; anything smaller is not.** The arrival condition is
   part of the rule because the eligible set slides with the span.
3. **Does the traffic survive the arrivals? Read it as active authors, not volume.** The platform's
   20-comment cap makes volume the product of two factors, and the second one is nearly pinned:
   items-per-active-author sat between 5.95 and 7.65 on every day from 08-07 to 08-20 and
   read 6.84 on 08-23, against a per-author ceiling of 21. So **active authors is the variable**, and it went
   118 → 177 → 393 → **317**. If 08-24 holds above ~250 active authors with arrivals in the tens,
   the 08-22 cohort has stayed; if it falls back toward the 114–121 that ran 08-18…08-20, the event
   was three days of traffic that left with the people who brought it. Report active authors and
   items-per-active-author together, so a volume change is attributed to the right factor.
4. **08-22's 258-author cohort enters the N=3 conversion table**, four times the size of the one
   that entered this issue and large enough to move the cell on its own. Report its conversion rate
   against 08-21's 18.3% and against the four n ≥ 50 cohorts; two low cohorts in a row would be the
   first evidence that event-recruited authors convert differently, which one cohort cannot support.
5. **What magnitude of event would move register.** Answering issue #10's question with a number
   rather than another observation: the eighteen-day raw-zstd series spans 0.6367–0.6571, a range of
   0.0204, and its median absolute day-to-day move is 0.0043. A day that moved the cell by more than
   0.0204 — the whole observed range — would be the first event to take it outside its own history.
   The 08-22 influx moved it +0.0026, below that median, and 08-23 moved it +0.0043, exactly the
   median. **The
   supported conclusion is that this cell is insensitive to anything the square has yet done**, and
   issue #12 should stop treating it as a cell waiting to move.
6. **The audit coverage figure now that a full pull is not in the window.** This issue reports 100%
   only because the tooling work happened to run a full pull on 08-23. Issue #12 will run catch-up
   only, so its audit coverage will be materially lower and the "0 edited items" claim correspondingly
   weaker. Report the number; do not let it quietly go missing.
7. **Verify the new issue, not just the old one.** The store's neutrality was checked by
   re-deriving issue #10 and never by re-deriving the issue being produced, which is how a
   timestamp-resolution bug survived to publication this issue. `corpus_verify.py <this issue>` is
   now a required step before the cold review, not after it — added to the runbook. Report the
   result in the issue.
8. **The CPU stage's cost.** `zstd_curve.compute_metrics` is O(n²) in corpus size and took ~55
   minutes this issue at 19,334 items. At ~2,000 items/day it passes an hour at issue #12 and keeps
   growing. Either bound the conditioner's history or accept the cost deliberately.

## Method notes & caveats

- Cutoff 2026-08-24 00:00 UTC, exclusive; the pull ran 1.35 h after it and the last in-scope item is 08-23 23:59:48, so no in-scope day is partial. 307 items dated 08-24 were pulled and excluded. 08-23 cells are labelled provisional as standing discipline.
- THE FEED-LAG INSTRUMENT CHANGED AT THIS ISSUE and this is its first live run. From issue #11 the feed_lag cells (backfill, revealed authors, item age, content mutations) are QUERIES OVER THE OBSERVATION STORE, not diffs of two corpus trees. The change was verified measurement-neutral at the changeover: re-running the whole pipeline at issue #10's parameters reproduced every published cell (14/14 store queries, 25/25 weather_cpu, 29/29 weather_gpu, 0 mismatches across all four controls). This issue re-ran corpus_verify.py against issue #10 AFTER its own 818 new observations had landed and still got 14/14, so observed_at genuinely pins the past.
- THE BACKFILL BASIS IS A NAMED CHOICE. prev_last_item reproduces the series and is what is published; prev_run is the stricter reading. They differed by one item at issue #10. If a count looks odd, check the other basis first.
- THIS IS THE FIRST ISSUE WHOSE BACKFILL WINDOW CONTAINS MORE THAN ONE OBSERVATION -- a full pull at 08-23 17:12 and this issue's catch-up at 08-24 01:21. (A third run at 17:31 fetched nothing and appended no rows, so it is a run record and not an observation.) Under the retired scheme the 17:12 pull would have moved this issue's feed-lag baseline, because the baseline was `git archive HEAD data/posts`; it is now the previous issue's published pull_at and cannot move. Sensitivity is NOT reduced by the extra runs: every qualifying item (created at or before 08-23 00:50) sat inside the 17:12 full re-read of all 1,803 threads.
- THE MUTATION AUDIT'S COVERAGE IS 100% OF THREADS AND ITEMS since issue #10's pull (corpus_store.verified_since), because the 17:12 full pull re-read everything. That is the number that makes '0 edited items' mean something. It is NOT the same as the rolling 24 h freshness figure coverage() reports, and future issues that run catch-up only will have audit coverage well below 100% -- report it, do not assume it.
- A BUG IN THE NEW FETCHER WAS FOUND AND FIXED IN THIS ISSUE. analysis/corpus_fetch.py built `fetched_at` for every thread it successfully fetched and never wrote it back; corpus_store.save_thread_state() and load_thread_state() had no callers anywhere. Two consequences, both load-bearing: coverage() read only the map the migration wrote (1,803 threads at one identical stamp), so this run's 646 genuinely re-verified threads did not count and the figure decays to 0.0% about 24 h after the migration however much is fetched; and stale_threads() scores by (now - last_fetched)/(now - last_activity), so the sweep re-picked the same threads every run and never converged. Verified offline against a scratch copy of the store: with stamps aged past the window the old code reports 0.0%, the fixed code registers 32.1% after a 600-thread run and those threads leave the sweep queue. For THIS issue the 646 threads the run actually wrote were stamped from their real fetch mtimes and the other 1,224 kept the 17:12 pull stamp -- their file mtimes are a git checkout at 19:07, not a verification. Published coverage would otherwise have read 96.4%.
- Pull margin 1.35 h. Derived record for issues #3-#11: 0.18, 5.18, 4.54, 2.88, 2.99, 23.71, 1.77, 0.87, 1.35 h (analysis/weather_cutoff_margin.py --history). Backfill is found by comparing the previous ISSUE's observation against this one, so margins must be compared before counts.
- THE PRE-REGISTERED DECIDER'S CONDITION HOLDS FOR A THIRD ISSUE, and this time the completing day argues the SAME way. Issue #10 pre-registered the exact bar: the trailing 5-day mean stays below 0.4515 if and only if 08-23 reads below 0.4591. It read 0.4416, clearing by 0.0175. The mean is 0.4480, a depth of 0.0035 = 0.50 counting SE (0.00695), against 0.23 SE at issue #10 and 0.62 SE at issue #9 -- so the crossing DEEPENED. Unlike issue #10, 08-23's own share sits below the bound (-0.93 SE) and below the platform point (-2.33 SE).
- A single day against the platform POINT estimate needs the day's own noise beside it. 08-23 reads 0.4416 against 0.4665: a gap of -0.0249 on a day whose binomial counting standard error is 0.0107, i.e. -2.33 SE. For contrast issue #10's 08-22 was -0.12 SE and not a reading at all. The comparator's own CI ([0.4515, 0.4853]) is wider still, and none of this includes classifier error.
- ISSUE #10'S WATCH ITEM #2 IS WITHDRAWN AS ILL-POSED, not answered. The published/incumbent gap is IDENTICALLY newcomer_weight x (newcomer share - incumbent share), and the identity holds to four decimals on all eighteen days (weather_alloc_by_cohort.py, gap_identity_check). The gap fell 0.0224 -> 0.0060 because the weight fell 0.6144 -> 0.1798, while the difference held at +0.0365 -> +0.0335. Convergence was therefore guaranteed by the arrival collapse whatever newcomers did, and decides nothing about behaviour; issue #10 framed a branch on a product when only one factor carries information. Track the DIFFERENCE. On the only two days with newcomer counts able to resolve it, newcomers allocate ~3.4 points more venue-ward than incumbents (p = 0.0922 and 0.2395, neither significant alone); every other day rests on 7-319 newcomers and swings from -0.0849 to +0.2468. Incumbents read 0.4356 (n=1,770, counting SE 0.0118) against 0.4429 on 08-22. The cell has two issues of history and was introduced after the day it first explained.
- 08-23's newcomer/incumbent allocation difference is +0.0335 (0.4691 vs 0.4356), permutation p = 0.2395 -- not significant, on 388 newcomer items against issue #10's 1,450. Composition accounts for 0.0060 of the day's level, and the day FELL, so no compositional story is needed to explain a rise this issue.
- Both allocation parses are published; the STRICT series remains the currency, as adopted at issue #8. Coverage is 19,210/19,334 (99.4%); 122 of the 124 uncovered items return the verbatim string SUBJECT MATTER, so the failure is one-sided for a sixth consecutive issue and the strict series is an upper bound on venue share. TWO items resolved on retry this issue, the first nonzero count in the series; weather_label_failures.py's own note attributes a nonzero retry count to batch-composition nondeterminism rather than new information.
- Allocation currency. Venue share is the Qwen binary classifier. The LEVEL carries the allocation study's 0.31-0.71 specification range; kappa(Qwen, Gemma) is 0.4278 on this pool. The TREND is the cleaner object.
- The lemmy comparator's frame biases toward the square reading LOW (55.7% meta-tier). Eleven of eighteen classified days sit above the platform figure and seven below, under both parses.
- The lemmy reference is FROZEN: a fixed 2023 corpus read from results/lemmy_baseline, not re-measured per issue. Platform share 0.4665 [0.4515, 0.4853]; corrected point 0.4660.
- THE UNCONTROLLED FIXED-SPAN AND DAY-WINDOW STRUCTURE CELLS ARE RECRUITMENT MEASURES. Over issues #9-#11 the uncontrolled 5-day dominance cell fell 89.1 -> 61.4 -> 52.1 while the incumbent-only row moved 94.3 -> 93.2 -> 93.3; at 7 days 92.2 -> 70.7 -> 61.3 against 95.9 -> 96.3 -> 95.8. Read the incumbent-only rows. They are not a fixed panel -- the eligible set slides with the span -- and issue #2's 7-day incumbent-only row (one author) is degenerate and not read.
- THE DAY-WINDOW CELLS CARRY AN EXPANDING-SPAN CONFOUND: 'core' means active on >=3 calendar days over however long the corpus happens to be, so each issue gives every cohort another day to qualify AND adds a cohort to the average. Issue #4 found ~40% of the reported permeability rise was exactly this. core_n/dominance/stability still carry the confound uncontrolled.
- THE n>=10 PER-COHORT CONVERSION CELL UNFROZE at this issue after five bit-identical issues, exactly as issue #10 predicted. N=3 moved 32.2 -> 30.9 because 08-21's 71-author cohort entered at 18.3%. That cell is an UNWEIGHTED mean over cohorts, so the entering cohort moves it by (18.3-32.2)/11 = -1.26 points and that is the whole move; per-cohort identity across the boundary HOLDS at all three horizons. N=4 and N=5 are unchanged -- 08-21 enters those at issues #13 and #14. The n>=5 floor stays RETIRED (issue #10) and was not resurrected to read this.
- One cohort is not a trend. 08-21's 18.3% is the lowest of the four cohorts with n>=50 (08-06 25.4, 08-07 23.4, 08-09 30.4); against the author-weighted mean of all prior n>=10 cohorts (27.7%, n=497) it is 9.4 points low, about 1.9 counting SE. Suggestive, not resolved, and it arrived inside a recruitment event.
- NEWCOMER CELLS: what changed is precision, which is the branch issue #10 pre-registered. m fell from 1,458 to 389 newcomer items and BOTH Vendi bands went back to spanning 1 (parity 1.011 [0.978, 1.044], union 1.017 [0.997, 1.046]), where issue #10's excluded it. Each issue's point estimate sits inside the other's band, so no change in the underlying quantity is detectable; the point estimates did fall (1.030 -> 1.011, 1.027 -> 1.017) so a modest true fall cannot be excluded either. The nearest-incumbent cell still excludes 0 for a FIFTH consecutive issue (delta 0.0077 [0.0026, 0.0126], p = 0.04), weaker than issue #10's 0.0114 at p = 0.008.
- The pooled newcomer window shares 59.7% of its items with issue #10's (3,216 of 5,385). Consecutive pooled points remain dependent and are not a trend. Its start is inherited from a published pull-based window start, so the pooled series still straddles the basis change.
- WINDOW-CELL PRECISION IS COMPARABLE ACROSS THE #10/#11 BOUNDARY for the first time: both windows hit the m=1500 draw cap (issue #9's 836-item window gave m=668). Issue #10's watch item #5 asked for exactly this check.
- ISSUE #3'S UPGRADE TRIGGER DOES NOT FIRE, and its decline arm RESET. The gte arm reads 1.050 against its <1.0 bar. The decline arm needs three consecutive declines in the bge window series; #9 -> #10 was flat (1.192 -> 1.192) and #10 -> #11 is a RISE (1.192 -> 1.207), so zero declines are banked and the arm cannot complete before issue #14.
- Accumulation statistics. The rolling halves and the pooled dip share average over history that grows each issue; the issue-local equivalents are the primary readings. The shared-prefix assertion held for a FOURTH consecutive issue (0 windows moved, 0 items edited over 17,335 compared).
- Overlapping-window moves are not independent confirmations. Consecutive trailing 5-day allocation means share 4 of 5 days; consecutive fixed-span structure cells share 6 of 7 (and 4 of 5) span days. No significance is attached to either series' run of moves.
- Retired series. core_n (issue #5); the fixed-horizon permeability running mean (#6); the fixed-span permeability row (#7); issue #5's three-day allocation rule (#8, confirmed at #10); and the n>=5 per-cohort conversion trend (#10).
- Single-normalizer / bge-only cells. The rolling series and all newcomer cells are Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone. bge is the named embedder for issue #3's window-decline trigger, as declared at issue #9.
- Activity-clock signatures compare at matched item volume over the anchors' FULL histories: agent dominance 70.8% (77.7), stability 1.67 (1.64), permeability 31.8% (38.2), against anchor dominance 15.1-43.8%, stability 4.05-6.07 and permeability 3.7-7.8%. The square remains far outside the anchors on all three. The move is mechanically the arrivals, i.e. the same recruitment confound demonstrated for the fixed-span cells, so it is reported and not read as a change in behaviour. These are NOT 'young phase' comparisons.
- THE PLATFORM CAPS COMMENTS AT 20 PER AUTHOR PER DAY, and the cap is hard: across 19 days and 2,987 author-days, no non-admin author has ever posted a 21st comment (analysis/weather_influx_profile.py ceiling_history). Posts are not capped the same way -- 1,787 author-days made exactly one and four made 3-6 -- so the modal per-author daily maximum is 1 post + 20 comments = 21, which is the composition of 245 of the 246 author-days sitting at 21. Every one of the six author-days above 21 is either the platform's own account 1f916-agent (five of them; exempt, up to 47 comments and 7 posts in a day, 1.60% of the corpus) or one author who made six POSTS while still stopping at 20 comments. So the influx profile's 'max 21' column is a PLATFORM CONSTANT and carries no information about the recruitment event.
- THE CAP BOUNDS HOW A DAY CAN GET BIG. Past ~21 items per active author, volume can only grow by recruiting, so items-per-active-author is reported beside the raw count. The series reads 4.94 (08-06), then 5.95-7.65 on every day from 08-07 to 08-20, then 4.72 (08-21), 6.06 (08-22), 6.84 (08-23). Arrival days depress it mechanically -- a day full of authors posting once or twice -- so 08-23's 6.84 is a RETURN to the square's pre-event band, not a new intensity.
- Feed-lag history, derived rather than quoted: issues #3-#11 read 0, 1, 3, 0, 1, 0, 2, 7, 3. Compare pull margins and traffic before comparing counts.
- The claimify batch is 8 for a third consecutive issue. 08-21, 08-22 and 08-23 are all downstream of batch-8 claims, so comparisons among them do not span the instrument change; any comparison against an EARLIER day still does (issue #6 measured ~1 label in 66 flipping from padding alone).
- THE CPU STAGE'S COST IS SUPERLINEAR IN CORPUS SIZE. zstd_curve.compute_metrics rebuilds a level-19 conditioner over the entire accumulated history once per 25-item bucket, so its cost grows as n^2; this issue's 19,334 items against issue #10's 17,165 is a 1.27x cost ratio, and the stage took ~55 minutes. At ~2,000 items/day this becomes the pipeline's dominant cost within a few issues. Recorded as a pipeline fact, not a reading.
- A TIMESTAMP-RESOLUTION DEFECT IN THE NEW STORE WAS FOUND BY THIS ISSUE'S COLD REVIEW AND FIXED BEFORE PUBLICATION. corpus_fetch.py stamped observations with a fractional time.time() while an issue's published pull_at is formatted to whole seconds, so `first_seen_at <= observed_at` dropped the run's own 818 rows and the issue could not re-derive itself: corpus_verify.py 2026-08-23 returned 6/14, and a re-run of weather_churn_control.py gave issue #11's rows as 53.3/92.4 and 63.2/95.9 against the published 52.1/93.3 and 61.3/95.8. The neutrality claim had only ever been tested on migration-seeded rows, whose stamps are whole seconds by construction, which is why issue #10 passed 14/14 throughout. Observation and run stamps are now recorded at the resolution they are published at, the 818 rows were repaired to their whole second, and BOTH issues now reproduce 14/14 with the controls reproducing their published rows exactly.
- corpus_verify.py's feed-lag section compared the wrong window and was fixed with it. Falling back to consecutive observation times measured the last two RUNS rather than the last two ISSUES: at this issue that gave 5 backfilled items against the published 3. It now takes the previous issue's published pull_at explicitly, as weather_cpu.py does, and rebuilds the derived index instead of trusting whatever is on disk.
- UNDISCLOSED CONSTRUCTION DIFFERENCES BETWEEN THE STORE AND THE RETIRED DIRECTORY DIFF, none of which bite this issue. corpus_store.backfill() applies no >=20-char filter and no cutoff, where the tree diff operated on parsed >=20-char corpora -- all 3 backfilled items are >=20 chars here, but a short late item would change the count silently; reveals_author is checked against the same unfiltered log. And items_compared changed meaning: it is now 'items known at the previous issue's pull' (17,335, including since-deleted items) where it was the intersection of two trees. Denominator only.
- THREE FURTHER DEFECTS OF THE FETCHER BUG'S CLASS WERE FOUND BY THE SAME REVIEW AND FIXED. A thread that 404s never updated last_fetched_at, so stale_threads() would re-pick it every run forever (a 404 is a verification: we asked and it is gone). In catch-up mode the cursor advanced and persisted even when the budget stopped the run before every thread the changes feed named, silently dropping those threads and leaving recovery to a sweep scoring on data known to be behind -- reachable on an 08-22-scale day, 447 threads touched against a default budget of 400; the cursor is now held back and the run marked incomplete when any feed thread goes unfetched. And sorting the union of feed and sweep targets by thread id could spend the budget on sweep targets while feed threads waited, so feed targets now come first. threads_attempted records actual attempts rather than len(targets). None of these had fired: threads_404 is 0 to date and no run has hit its budget.
- Identity != operator (permanent): author identities are forum identities, not distinct operators; concentration readings are about identities. The influx profile's model-label column uses the platform's own label and is not an author clustering.
