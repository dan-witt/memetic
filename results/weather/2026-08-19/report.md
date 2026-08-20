# 1f916 weather · 2026-08-19 (issue #7)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: full pull at 2026-08-20 02:59 UTC (last in-scope item 08-19 23:54:07), hard cutoff
**2026-08-20 00:00 UTC**. In scope: **13,247 items** (≥ 20 chars), 529 authors, Aug 5 → Aug 19
(complete, 3.0 hours of margin). Issue window (since issue #6's **pull**, 08-19 02:50): **521
items** inside one calendar day. Four pre-registered triggers fired and three did not. The
allocation excursion completed its third day, firing both of issue #5's rules, so **below-platform
self-allocation is now a sustained finding by the criterion set two issues ago** — and the
classifier failure behind the label-coverage watch item turned out to be deterministic and
**one-sided**, which makes the published series an upper bound and moves the finding further in the
direction it already points. Inflow's "08-18 was noise" trigger fired too, on a record-low 5 new
authors. The three that did not fire are the ones that would have confirmed existing readings: the
sub-forth dip rate **fell** instead of holding in the 40s, the two controlled-dominance widths
disagreed again, and no placement trigger came close. Separately, the shared-prefix assertion
**fired for the first time in seven issues**.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow falling from 224/day at founding to 5; register flat well below the human band floor; daily venue share falling out of its prior band and ending three days below the lemmy.world platform line.](figure.png)

## Readings

**Allocation — the pre-registered threshold is met, and the comparator's known bias points the
same way.** The series ran 0.4865 (08-15) → 0.4720 (08-16) → 0.4484 (08-17) → 0.4508 (08-18) →
**0.4367** (08-19). That is a third consecutive day below the 0.456–0.548 band that held for nine
days through issue #4, and the lowest daily value the series has recorded (previous low 0.4484 on
08-17). Issue #5's rule for a level shift was one further day at or below 0.456; it landed.

Against the Usenet anchors' Qwen band (0.085–0.221) the day reads 2.0–5.1× high. Against
**lemmy.world's founding month — a human *platform* that also had to run itself, 0.4665 on the
identical classifier and prompt ([`lemmy_baseline`](../../lemmy_baseline/report.md))** — 08-19
reads **0.936**, a third straight day below the human platform line after 0.961 (08-17) and 0.966
(08-18). Read against the interval rather than the point (0.4665 [0.4515, 0.4853]
author-clustered), all three days also fall clear of the **lower bound** 0.4515: 0.4484, 0.4508,
0.4367. Issue #5 set three consecutive such days as the threshold for calling this a sustained
period of below-human self-allocation. **All three are now in hand.** Over the full 14 classified
days, 10 sit above the platform point estimate and 4 below.

That is the pre-registered criterion, and it is worth being exact about what it does and does not
buy. The comparator's own frame is **55.7% meta-tier**, a property of which lemmy.world communities
existed when the exodus landed rather than of the platform's nature, and it makes the human
benchmark *more* self-referential than a neutral human platform would be. The known direction of
that bias is toward the square reading low against it. So the threshold firing is **not**
independent evidence that the square is unusually outward-facing; it is a pre-registered rule
firing on a comparator biased in the direction of firing. The defensible statement is the narrow
one: by the rule set two issues ago, on the comparator as measured, the square has now spent three
consecutive days allocating less attention to itself than the human platform founding did.

**Level caveat unchanged**: the absolute number carries the allocation study's 0.31–0.71
specification range; the lemmy comparison holds classifier and prompt fixed on both sides but
inherits it.

**Direction within the excursion is still not decidable.** 08-19 is 0.0141 below 08-18, and four
of the five day-over-day moves since 08-14 are negative — but a 4-of-5 sign count is what fair-coin
signs produce 18.8% of the time (`analysis/weather_trend_tests.py`), and that figure is an *upper
bound* on how impressive the run is, because autocorrelation makes runs cheaper rather than dearer.
08-18 was itself a reversal. The decidable statement is about the level and the threshold, not the
slope.

**Label coverage — the failures are deterministic, identical and one-sided, so the published series
is an upper bound.** Issue #6 found that an unparseable classifier answer caches nothing and is
retried, and set the trigger: *if that count grows rather than converges, the classifier prompt —
not the cache — is the problem.* It grew, 72 → **83**, and the retry side is starker than the count
suggests. The delta pass classified **819** items — 746 valid-claim items on 08-19 plus **73**
retries on already-published days — and **not one retry resolved**. The published-day backlog is
the same 72 items it was last issue, item for item, plus one edited item re-labelled;
`published_days_moved` is empty.

So issue #6's watch item is answered, and `analysis/weather_label_failures.py` answers *why*.
Re-running the frozen prompt over all 83 uncovered items returns **the same string 83 times out of
83**: `SUBJECT MATTER`. Not a refusal, not garbage — the second branch of the question the prompt
itself asks ("…or about its SUBJECT MATTER or the outside world?"), echoed back verbatim instead of
the one word the prompt demands. Three things follow.

First, **retrying is inert.** Generation is greedy, so the same item under the same prompt returns
the same answer every issue; the only way a retry can ever resolve is batch composition shifting
the padding, which is exactly the one-in-sixty-six issue #6 observed. The retro-movement channel
issue #6 discovered is real but has roughly a 1% hit rate, and this issue it fired zero times.

Second, **the missing labels are not missing at random.** Every one is a WORLD answer. Dropping
them therefore inflates venue share, by a computable amount: keep the venue count and put the
uncovered items back in the denominator and the series reads 0.5446 (08-06) … 0.4673 (08-16),
0.4467 (08-17), 0.4466 (08-18), **0.4303** (08-19). Every day moves down, by 0.0006 to 0.0064.

Third, the correction **strengthens this issue's headline rather than threatening it** — and the
comparator side is what makes that check honest. The frozen lemmy corpus was classified with the
identical prompt and model, so it carries the same bias, and correcting one side only would be a
rigged comparison. `weather_lemmy_ref.coverage_bound()` bounds the comparator without re-measuring
it: 55,152 of 55,223 founding-month items were classified, so at most 71 were dropped (0.13%), and
counting every one of them WORLD moves the platform figure from 0.4665 to **0.4659** — a −0.0006
move against the square's −0.0064. Corrected on both sides, 08-19 reads 0.4303 against 0.4659, i.e.
**0.924** rather than 0.936. The shortfall widens.

**What this issue does *not* do is change the currency.** The published series stays on the strict
parse, because every cross-issue comparison and the frozen comparator were computed under it and
switching mid-series would move all fifteen days at once. Issue #8 should adopt a parse that
accepts the observed WORLD phrasings and republish the whole series under both, so the break is
documented rather than silent. Its size is now known in advance: at most 0.0064 on any day,
uniformly downward, and it moves no threshold conclusion in this issue — under the corrected series
the same 10 of 14 days sit above the platform point estimate, and the three sub-0.4515 days remain
sub-0.4515.

**Structure — inflow set a record low and issue #6's "noise" trigger fired.** New authors per day:
8 (issue #6) → **5**, the lowest of the series (the previous low was 6, on 08-05 and 08-17).
Newcomer item-share: 0.055 → **0.012**, less than a third of the previous low (0.038). Issue #6's
rule was explicit: *two more days at or above 8, or a newcomer item-share above 0.076, would say
the collapse has bottomed; a return to 6 or below says 08-18 was noise.* **The last of those
fired.** 08-18's uptick to 8 does not survive contact with 08-19, and no floor is established —
5 sits at the bottom of the 5–11 band the series has occupied since 08-14, and on counts this small
the noise is about ±2 authors, so this is one point at the low end of an existing scatter and not
by itself a new regime. Daily item volume continued to erode: 994 → 934 → 794 → 797 → 759 → **746**
over six days, non-monotonically. Active authors **rose to 121** (114), the top of the 112–123 scatter of the last five days.

The published day-window cells moved as they always do — core_n 210 → 218, dominance 88.8 → 89.4,
stability 1.24 → 1.21, permeability 43.9 → **46.9** — and still carry the expanding-span confound,
so they are reported and not read. The permeability cell is worth one sentence anyway, because it
demonstrates the confound a **second** consecutive time: the published average draws on the
*identical ten cohorts* it drew on in issues #5 and #6, so with membership constant its 43.9 → 46.9
rise can only be observation length. (Issue #4's cell drew on seven cohorts, so #4 → #5 was not a
membership-fixed transition; #5 → #6 and #6 → #7 are the two that are.)

Under the fixed-observation-span control:

| fixed span | #1 | #2 | #3 | #4 | #5 | #6 | **#7** |
|---|---|---|---|---|---|---|---|
| core dominance %, 7-day | 75.8 | 79.2 | 83.0 | 85.8 | 91.3 | 91.8 | **91.7** |
| core dominance %, 5-day | 77.1 | 79.3 | 84.3 | 86.4 | 87.6 | 88.4 | **91.0** |
| stability ratio, 7-day | 1.62 | 1.50 | 1.42 | 1.34 | 1.24 | 1.25 | **1.19** |
| stability ratio, 5-day | 1.61 | 1.51 | 1.43 | 1.35 | 1.32 | 1.32 | **1.25** |

**The two widths disagree about dominance for a second consecutive issue, so neither reading is
available.** The 7-day span posted its first *fall* of the series (−0.1) while the 5-day span
posted its largest rise since #3 (+2.6). Issue #6's rule was that a second consecutive near-flat
issue *at both widths* would replace "core concentration is rising" with "it has plateaued near
92%", and that disagreement again means neither is available. Disagreement is what happened, so
neither is claimed. **Controlled stability fell at both widths** (1.25 → 1.19 and 1.32 → 1.25),
which retires issue #6's "first non-decline" as a one-issue wobble rather than a break in the
series.

**The fixed-span permeability row is retired as a cross-issue series this issue.** It reads 43.7 →
52.2 at 7 days and 47.3 → 54.6 at 5 days, and those jumps are not interpretable — though not for
the reason a first look suggests. The *populations* are nearly the same: the 5-day cell's eligible
cohorts hold 180 authors at issue #6 and 161 at issue #7, sharing 152 of them (Jaccard 0.80; 0.92
at the 7-day span). The defect is **reassignment**, not turnover. An author's "first window" is
re-derived *relative to the span*, so as the span slides the same people are sorted into different
cohorts and their conversion is judged against a different window: issue #6's 130-author "08-14"
cohort is largely issue #7's 123-author "08-15" cohort. The cell therefore re-partitions a stable
population every issue, which is the same composition defect the fixed-horizon running mean was
retired for in issue #6, wearing different clothes. The row is still emitted and is not read. Dominance and stability are
span-level rather than cohort-level and do not carry the term.

**Per-cohort conversion — the primary horizon is frozen, and not just for one issue.** Issue #6
pre-registered N=3 as primary. At that horizon the cell is **bit-identical to issue #6** — 32.2,
r = +0.0908, p = 0.0444 on the same 497 authors over the same 10 cohorts — and per-cohort identity
HOLDS at all three horizons. That is issue #6's number re-reported, not a replication; a frozen
statistic cannot corroborate itself. N=4 is likewise unchanged (37.6, r = +0.0674, p = 0.1373).
Only N=5 moved, 38.3 → **41.7**, for the one reason the retirement predicts: the 08-15 cohort's
five-day window closed and it entered at 72.7% on **eleven authors**; over the nine shared cohorts
the cell reads 38.3, unchanged. Its trend moving to r = +0.0922, p = 0.0402 is that one small
cohort.

**Why nothing entered needs stating plainly, because it is a construction choice this series has
never disclosed.** `weather_permeability_control.py` counts a cohort only if it has **n ≥ 10**
authors. Two cohorts *did* complete their N=3 window by this cutoff — 08-16 (n=7, 14.3%) and 08-17
(n=6, 50.0%) — and were silently dropped, as 08-05 (n=6) has been at every horizon since issue #1.
So "no cohort entered" is the floor talking, not the calendar. The floor is not hiding a different
answer: recomputing N=3 at a n ≥ 5 floor admits all three and gives r = +0.0873, p = 0.0477 over 13
cohorts and 516 authors — the same direction, the same failure to establish. But the **structural**
consequence is real, and the watch items had it wrong: with inflow now at 5–8 authors a day, no
future cohort will reach n = 10, so the pre-registered primary horizon is frozen **indefinitely**,
not paused for an issue. Issue #8 has to either lower the floor with the small-cohort caveat
attached or retire the trend test; carrying it forward unchanged means re-reporting 0.0908 every
issue until inflow recovers.

**Direction still positive, effect still not established, and this issue adds no new evidence
either way.**

**Newcomer — the per-issue cell went dark again, and the pooled replacement is measurable.** The
window carries **9** newcomer items against 512 incumbent. That is not near the floors, it is far
below them (m ≥ 100 Vendi, m ≥ 50 NN), and it is under a quarter of issue #6's already-dark 42.
Issue #6 pre-registered the response rather than a second skip: pool the window over the last three
issues. `analysis/weather_newcomer.py` does that, and now also holds the per-issue cell
construction, which `weather_gpu.py` imports rather than duplicates. Two different things license
the numbers below, and they are worth separating. The standalone reproduces the pipeline's 9/512
split and its skip decision exactly — that check covers the **split and the floors**, not the Monte
Carlo, because the pipeline hands the per-issue cell its own already-consumed generator (preserving
the construction of issues #1–#5) while the standalone seeds a fresh one. Nothing turns on that
here, since both per-issue cells are skipped and no band is published from that path. The **pooled**
cell is seeded fresh from `default_rng(0)` in *both* paths, so its numbers are bit-identical whether
the pipeline or the standalone produces them.

The pooled window is the **contiguous** interval from issue #5's window start (08-15 05:10) to the
cutoff — 4.78 days, **423 newcomer items against 3,304 incumbent** — not the union of three issue
windows. Each issue's window begins at the *previous* issue's pull, so a union would leave holes
(225 items on 08-19 alone sit between issue #6's cutoff and its pull and enter no issue window
ever), and those holes fall at a fixed time of day, which would make a stitched sample diurnally
skewed on top of gappy.

| pooled cell (K=3; 423 newcomer / 3,304 incumbent) | reading |
|---|---|
| within-pool parity | **0.992** [0.957, 1.018] |
| union over incumbent | **1.002** [0.975, 1.027] |
| nearest-incumbent distance, matched pools | Δ **0.0092** [0.0047, 0.0137] vs null [−0.0077, 0.0073], p = **0.036** |

Newcomer claims spread internally about as widely as incumbent claims, and adding them to the
incumbent pool does **not** raise its effective distinct content — but they sit measurably
**farther from the incumbent cloud** than incumbents sit from each other, by about 3.4% of the base
distance (0.2707). The summary is *displaced but not diversifying*: newcomers say things a little
off to one side of what incumbents say, and either not enough of it or not differently enough from
each other to widen the community's overall spread.

Two disciplines on that p = 0.036. It is a single nominal test on a cell with no prior issues, so
there is nothing to correct for and nothing to compare against. And it is **not** like-for-like with
the closest published thing: issue #5's per-issue cell read Δ 0.0051 [−0.0013, 0.0111], p = 0.364
on 221 newcomer items, and this pooled set is a superset of those newcomers plus four further days
of arrivals with roughly double the queries — so part of the sharper p is power, not signal. **The
pooled cell starts its own series at issue #7 and is not a continuation of issues #1–#5.**

**Placement — the full-pool narrowing stopped.** Full-pool bge: lisp **1.229** (1.230), sci
**0.657** (0.657), hn **0.611** (0.610); gte lisp **1.062** (1.061) and mpnet lisp **1.264**
(1.253). Across issues #2 → #6 no embedder's full-pool lisp cell ever moved up; **this is the first
issue in which one did, and two did.** Every one of those moves is nonetheless far inside the
cell's own band (bge full lisp [1.202, 1.269]), so this is the absence of a further step rather
than a reversal. Whether the narrowing has ended or merely paused is not decidable on one issue.

Window-only cells, judged against the right comparator — the one-day windows of issues #4 (m=774)
and #6 (m=424), never issue #5's three-day one — are **uniformly narrower than #6 and mixed against
#4**: bge lisp 1.172 (#6 1.200, #4 1.185), sci 0.653 (0.675, #4 0.637), hn 0.615 (0.625, #4 0.594);
gte lisp 1.031 (1.051, #4 1.044); mpnet lisp 1.159 (1.194, #4 1.220). Against #4 all three lisp
cells sit lower and the sci/hn cells split, so there is no single direction to read there. Issue #3's upgrade trigger needs a third consecutive window decline or a gte
window cell below 1.0. Read on like-kind windows only, as issue #6 required, the bge series is
1.185 → 1.200 → **1.172** — one decline after a rise, not three — and gte stays above parity at
1.031, though its 5th percentile is now **1.002**, the closest that cell has come to touching 1.
**Neither condition fired**; the gte lower bound is worth carrying forward.

**Idea series — the dip rate fell, and the shared-prefix assertion fired for the first time.**
Rolling claim-Vendi/W halves read 0.1351 → **0.1295** (issue #6: 0.1350 → 0.1295), so the
cross-issue second-half series is #2 0.1343 → #3 0.1323 → #4 0.1324 → #5 0.1298 → #6 0.1295 → **#7
0.1295** — unchanged to four decimals, so issue #6's record low was matched, not extended. The cell
remains an accumulation statistic and is reported for continuity, not read. Issue #6's restated
corridor trigger is a half-window mean below forth's **0.1269**; at 0.1295 the series sits 2.0%
above that line, inside the forth-to-sci corridor where it has been every issue.

The issue-local cell is the one that moved, and it moved hard. Over the **19 windows this issue
added**, the sub-forth dip rate is **10.5%** (2/19), against 42.1% over #6's 19 windows and 47.6%
over #5's 63 — and the new-window mean rose to **0.1335** (#6 0.1299, #5 0.1276). That series mixes
window kinds and should be read with the labels on: #5's windows came from a **three-day** issue
window, #6's and #7's from **one-day** windows, so the only like-kind comparison here is #7 against
#6, which is the pair the test below uses. It is the lowest rate the cell has recorded since issue
#2, but that ranking spans both kinds. Issue #6's
watch item asked whether a third issue in the 40s would make "roughly half of all windows now dip
below the nearest anchor" a standing reading. **It did not.** But the change is not formally
distinguishable either: 2/19 against 8/19 is Fisher two-sided p = 0.0625
(`analysis/weather_trend_tests.py`), and the 120-item windows advance by 40, so each issue's
nineteen windows carry roughly six or seven independent observations — which makes Fisher on the
nominal n *anti-conservative*, so a test that already fails to reach significance fails a fortiori.
Direction clear, significance not claimable — and #5's 47.6% now reads more like a local excursion
than a plateau. The pooled share fell for the first time, 23.9 → 23.1%, which is
composition rather than behaviour.

**The prefix assertion earned its keep.** `weather_dip_rate.py` checks that the shared prefix of
two consecutive issues' rolling series is bit-identical, because the whole per-issue decomposition
depends on the past not moving. After six clean boundaries it **fired**: 3 of the 310 shared
windows changed. The cause is not a mystery, because a second instrument caught it independently —
the feed-lag block reports exactly one post-publication edit, `post:1197` on 08-18 20:38:08, cut
from 2,384 characters to 246. Its cached claim was evicted and re-generated, and the three moved
windows (indices 307–309, 08-18 19:17 / 21:19 / 21:29) are **exactly** the three that contain it,
which is the signature a single edited item leaves at W=120 and stride 40. No other window moved.
**None of the three crossed the forth anchor**, so issue #6's published dip count of 8/19 stands;
its new-window mean would read 0.1296 rather than 0.1299 on current data. The decomposition
survives, with the drift disclosed and bounded rather than assumed away. `weather_dip_rate.py` now
prints which windows moved, by how much, and whether any crossed the anchor, because a bare
"VIOLATED" is not actionable.

**Register — flat, at the top of its own narrow range.** Daily raw zstd for the new day: **0.6509**
(08-17 0.6445, 08-18 0.6480). That is the second-highest daily value of the series and effectively
ties 08-08's 0.6510, but the whole fourteen-day series (08-05 falls below the 50-item floor) spans
0.6367–0.6510 — 0.014 wide — and sits
0.053 below the 0.704 human band floor it has never approached. A single day at the top of a band
that narrow is not a trend. **One previously published figure is revised**: 08-18 was published at
0.6481 and now reads **0.6480**, moved by the `post:1197` edit above. This is the fourth-decimal
register movement issue #4 predicted when it built the mutation detector, observed for the second
time.

**Feed lag — a third non-zero boundary, and the pattern across all five is a pull-boundary race.**
This issue finds **1** backfilled item, on 08-19, with an item age at the missed pull of **0.01
hours** — about 36 seconds. That is the third non-zero boundary the instrument has measured, not
the first: issue #4 published 1 item (aged 0.04 h) and issue #5 published **3** (aged 0.05–0.07 h,
and **2 new authors revealed**, which issue #5 correctly called a new maximum). Across the five
boundaries the block has measured — issues #3 through #7 — the totals are 0, 1, 3, 0, **1**: five
items, every one of them **under four minutes old** at the missed pull. So the record is not "the
feed never lags"; it is that when an item is missed it was created in the last minutes before the
pull, which is a boundary race rather than a lagging feed. This issue's single item revealed **0
new authors**, so no cohort, inflow or churn cell changes — but issue #5 shows that is not
guaranteed, and the check is run for that reason. Trailing-day numbers stay labelled provisional as
standing discipline. Content hashing compared **12,725** items and found the single edit described
above.

## Issue #6's watch items, answered by name

1. **The allocation excursion needs one more day.** — **it came, and both thresholds fired.** 08-19
   at 0.4367 is at or below 0.456, making the level shift by issue #5's rule, and it is the third
   consecutive day below the lemmy lower bound 0.4515, completing the three-day threshold for a
   sustained period of below-platform self-allocation. It is also the series' record low. The
   comparator's known meta-tier bias runs in the same direction as the finding, which is stated
   above and is the main reason not to read it as more than the rule being met.
2. **Is the inflow floor real?** — **no; the noise reading fired.** 8 → **5** new authors, below
   issue #6's "6 or below says 08-18 was noise" threshold, with newcomer item-share 0.055 → 0.012.
   No floor is established in either direction; 5 is the low end of the 5–11 band held since 08-14.
3. **Controlled dominance and stability.** — **the widths disagreed again, so neither reading is
   available**, exactly as issue #6 specified: 7-day 91.8 → 91.7 (its first fall) against 5-day
   88.4 → 91.0. Stability fell at both widths (1.25 → 1.19, 1.32 → 1.25), so issue #6's first
   non-decline did not persist.
4. **The newcomer instrument is dark.** — **dark again at 9 items**, and the pre-registered pooled
   window was built and run: 423 newcomer against 3,304 incumbent items over 4.78 days, all three
   cells computable. It is a new series, not a continuation.
5. **Label coverage.** — **the count grew, 72 → 83, and issue #6's trigger is correct: the prompt
   is the problem.** All 83 return `SUBJECT MATTER`; zero of 73 retries resolved; the failure is
   one-sided so the published series is an upper bound; the corrected parse is pre-registered for
   issue #8 with the comparator's side bounded at −0.0006.
6. **Dip rate, now that it is measured per issue.** — **it fell to 10.5%** (2/19), not a third
   issue in the 40s. Not formally distinguishable from #6's 42.1% (Fisher p = 0.0625, windows
   overlap threefold), but the direction is unambiguous and #5's 47.6% now looks like an excursion.
7. **Per-cohort conversion, with the horizons pre-registered.** — **N=3 could not update, and
   cannot update again at current inflow.** N=3 and N=4 are bit-identical to issue #6 and
   per-cohort identity holds; only N=5 moved, entirely because one 11-author cohort entered. The
   reason nothing entered is an undisclosed n ≥ 10 cohort floor, not the calendar: 08-16 (n=7) and
   08-17 (n=6) completed their windows and were dropped. At a n ≥ 5 floor the reading is unchanged
   (r = +0.0873, p = 0.0477). No new evidence this issue, and none available next issue either
   unless the floor changes.

## Watch items for issue #8

1. **Adopt the corrected parse and republish the series under both.** The failure mode is
   characterised (83/83 `SUBJECT MATTER`, one-sided, deterministic) and the break is bounded
   (≤ 0.0064 on any day, uniformly downward, no threshold conclusion moved). Issue #8 should accept
   the observed WORLD phrasings, recompute all fifteen days *and* the comparator's founding month
   under both parses, and publish them side by side. Left unmade a third issue, the report is
   knowingly publishing an upper bound as a point estimate.
2. **Does the level hold below the platform, now that the threshold has fired?** The question
   changes from "is it a shift" to "is it a floor": two further days below 0.4515 make it a five-day regime; a return above 0.456 makes 08-17..08-19 a three-day dip and makes issue #5's
   three-day rule a false positive worth re-examining.
3. **Inflow after a record low.** 5/day and a 0.012 newcomer share are both series lows. A second
   consecutive day at or below 6 makes the collapse a regime rather than a scatter; a return to 8+
   means the last two issues have been reading noise in both directions.
4. **The pooled newcomer cell's second point.** Δ = 0.0092 (p = 0.036) is one nominal test. Issue
   #8's pooled window will overlap this one heavily, so the two points are strongly dependent and
   must not be read as a two-point trend; report the overlap fraction alongside the cell.
5. **The gte window cell's lower bound** reached 1.002, the closest that cell has come to parity.
   Issue #3's trigger is the *median* below 1.0; a band touching parity is worth watching a step
   before the trigger.
6. **Was the dip-rate collapse real?** 10.5% after 47.6% and 42.1% is the largest single-issue move
   the cell has made. A second issue in the 10s–20s says #5 and #6 were the excursion; a return to
   the 40s says #7 was.
7. **The per-cohort trend test needs a decision, not another carry-forward.** Under the
   undisclosed n ≥ 10 cohort floor the pre-registered primary N=3 cannot update again at current
   inflow, so issue #8 must either lower the floor (r = +0.0873, p = 0.0477 at n ≥ 5, same reading)
   and say so, or retire the test. Re-reporting a frozen 0.0908 as though it were a fresh
   measurement is the failure mode this series retired two other cells for.
8. **Prefix drift, now that it fires.** One edit moved three windows this issue. If edits become
   routine the per-issue decomposition needs the drifted windows excluded rather than merely
   disclosed, and the register cells need the same treatment.

## Method notes & caveats

- **Cutoff** 2026-08-20 00:00 UTC, exclusive; the pull ran 3.0 h after it and the last in-scope
  item is 08-19 23:54:07, so no in-scope day is partial. 08-19 cells are labelled provisional as
  standing discipline.
- **One-day window** (521 items, 08-19 02:50 → 23:54). Window-only cells are comparable in kind to
  the one-day windows of issues #4 (774 sampled) and #6 (424) and NOT to issue #5's three-day one.
  The window starts at issue #6's PULL, so the **225** in-scope items of 08-19 00:00–02:50 enter
  every full-pool cell and no issue's window cells, ever; their diurnal position differs from the
  rest of the day, so window-only cells are not a random sample of 08-19 either.
- **No per-issue newcomer cells** for the second issue running: 9 newcomer items against floors of
  m ≥ 100 (Vendi) and m ≥ 50 (NN). Replaced by the pooled-window cell, which is a **new series**,
  not a continuation of issues #1–#5.
- **The pooled newcomer window overlaps its neighbours by construction.** It spans 4.78 days and
  three issue windows; issue #8's will overlap it heavily, so consecutive pooled points are
  strongly dependent and must not be read as independent observations.
- **Delta pipeline.** Claims and allocation labels are cached by `kind:id`; 747 items claimified
  this issue, including 1 re-claimified after an edit evicted its cache entry. Frozen anchors are
  never re-measured and their hashes are unchanged.
- **The published allocation series is an UPPER bound.** Every unparseable classifier answer is the
  verbatim string `SUBJECT MATTER` — a WORLD answer the strict parse discards — so dropping the 83
  uncovered items inflates venue share by 0.0006 to 0.0064 per day. The corrected series is
  reported alongside, not substituted: the frozen comparator was classified under the same strict
  parse, and correcting one side only would be a rigged comparison.
- **The comparator's coverage bound is a BOUND, not a correction.** 55,152 of 55,223 founding-month
  items were classified; counting all 71 of the difference as WORLD is the worst case (−0.0006).
  Part of that difference is invalid claims rather than unparsed answers, so the true move is
  smaller.
- **Retries are inert.** Greedy decoding means an unparseable item returns the same answer every
  issue; only batch-composition changes to the padding can flip one, which is the ~1-in-66 issue #6
  saw and the 0-in-73 this issue saw. Label coverage is 13,164/13,247 (99.4%).
- **The lemmy comparator's frame biases toward this issue's headline.** Its 55.7% meta-tier
  composition makes the human benchmark more self-referential than a neutral human platform would
  be, and the direction of that bias is toward the square reading below it. The three-day threshold
  firing is a pre-registered rule being met, not independent evidence.
- **Single-normalizer / bge-only cells.** The rolling series and all newcomer cells are
  Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone.
- **Allocation currency.** Venue share is the Qwen binary classifier. The LEVEL carries the
  allocation study's 0.31–0.71 specification range; κ(Qwen, Gemma) is 0.4278 on this pool. The
  TREND is the cleaner object.
- **The lemmy reference is frozen.** lemmy.world's founding month is a fixed 2023 corpus read from
  `results/lemmy_baseline/results.json` by `analysis/weather_lemmy_ref.py`; it is not re-measured
  per issue. Its platform share is a point estimate with a band, 0.4665 [0.4515, 0.4853].
- **Accumulation statistics.** The rolling halves and the pooled dip share average over history
  that grows each issue; the issue-local equivalents are the primary readings and the pooled forms
  are kept for continuity. Every per-issue decomposition depends on the shared prefix not moving,
  which `weather_dip_rate.py` and `weather_permeability_control.py` assert rather than assume —
  and the former **fired this issue**, bounded to 3 windows by one edit, none crossing the anchor.
- **Retired series.** core_n (issue #5); the fixed-horizon permeability running mean (issue #6);
  and, from this issue, the **fixed-span permeability row** — not because its population turns over
  (the 5-day cell's cohorts share 152 of ~170 authors across the boundary, Jaccard 0.80) but because
  the span slides and **reassigns** the same authors into different span-relative cohorts each
  issue, which is the same composition defect the fixed-horizon mean was retired for. Dominance and
  stability are span-level and are retained.
- **The per-cohort trend test** is three correlated horizons of one hypothesis with no multiplicity
  correction; N=3 is the pre-registered primary per issue #6. This issue N=3 and N=4 are frozen and
  cannot corroborate anything. **A previously undisclosed n ≥ 10 cohort floor** is why: 08-16 (n=7)
  and 08-17 (n=6) completed their N=3 windows and were dropped, as 08-05 (n=6) always has been. At
  n ≥ 5 the reading is unchanged (r = +0.0873, p = 0.0477), but at 5–8 new authors a day no future
  cohort clears n = 10, so the primary horizon is frozen indefinitely rather than for one issue.
- **Activity-clock signatures** compare at matched item volume over the anchors' FULL histories:
  agent dominance 82.6% (83.3), stability 1.42 (1.41), permeability 37.6% (36.6), against anchor
  dominance 15.1–43.8%, stability 4.05–6.07 and permeability 3.7–7.8%. These are not "young phase"
  comparisons.
- **Feed-lag history.** This issue's 1 backfilled item is the **third** non-zero boundary of five
  measured (issues #3–#7: 0, 1, 3, 0, 1), not the first; issue #5's three items revealed 2 new
  authors. All five items were under four minutes old at the missed pull.
- **The dip-rate series mixes window kinds.** #5's rate is over a three-day issue window, #6's and
  #7's over one-day windows; only #7-vs-#6 is like-for-like, and that is the pair tested.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators; concentration readings are about identities.
