# 1f916 weather · 2026-08-28 (issue #15)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-29 01:34 UTC (last in-scope item 08-28 23:55:39), hard
cutoff **2026-08-29 00:00 UTC**. In scope: **31,512 items** (≥ 20 chars, moderation placeholders
excluded), 1,336 authors, Aug 5 → Aug 28, complete, 1.58 hours of margin. Issue window:
**2,171 items across one calendar day**, 08-28 — the same width as issues #9–#13, and one day
narrower than issue #14. This is the first issue on a stable currency since the placeholder
re-baseline, and two of its readings are the controls that change came with. **The shared-prefix
assertion resumes and passes exactly**: 0 of the 731 windows issue #14 published moved.
**Issue #8's decider is deeper again** — the trailing five-day mean reads **0.4277** at 08-28
against a bound of 0.4515, a depth of **5.29 counting SE**, and the mean has now been below the
bound at eight consecutive day-endpoints. Two pre-registered items resolve against the direction
their published series pointed. **Issue #3's placement decline arm fires on the published
per-issue window series and is not treated as a completion**: at matched window width and one
basis the last five one-day windows read 1.219, 1.209, 1.210, **1.152**, **1.170** — a one-day
step at 08-27 that partly recovers, not three consecutive declines. And **the backfill rate fell
sharply rather than rising**, once the count is divided by the population it can actually come
from. This issue also takes issue #14's watch item #4 decision: **the sub-forth dip rate is
demoted to a footnote and the window-level median becomes the published idea-series cell.***

![Four panels: idea diversity oscillating inside the forth-to-sci corridor with its newest windows near the lower edge; author inflow falling to 26 after the five-day event; register easing to 0.6581 just below its series high; daily venue share at 0.4295, below the lemmy.world platform line for an eighth consecutive day.](figure.png)

## Two controls the re-baseline owed, and both are now in

**The shared prefix is bit-identical.** Issue #14 excluded moderation placeholders, which re-cut
every 120-item rolling window and moved 611 of the 618 windows issue #13 had published. That
suspended the series' standing assertion for exactly one issue, and issue #14's watch item #3 said
anything other than a clean pass here would be a defect rather than a currency change. Of the
**731** windows issue #14 published, **0 moved**. The per-issue decomposition is comparable again,
and the historical violations stand where they were: issue #7 (3 windows, one edited item, no
crossing), issue #12 (13 windows, one crossing), issue #14 (the re-baseline itself).

**The backfill denominator was wrong, and correcting it reverses the reading.** Issue #14 recorded
13 backfilled items, the largest count on record, and set the next comparison at 2.8 per thousand
*window* items. This issue's 11 items over 2,171 window items is 5.07 per thousand, which on that
basis reads as a near-doubling. The denominator is mis-specified. A backfilled item is one the
**previous** pull should have caught and did not, so it can only come from the stretch that pull's
coverage had already reached: items created after the previous issue's cutoff but at or before the
previous corpus's last item. The width of that stretch is the previous pull's **margin**, not this
issue's window width — issue #14 covered two calendar days and so divided the same boundary race
by twice as many items.

`analysis/weather_backfill_exposure.py` publishes the count with its exposure and derives the pair
for every published issue. It reproduces all eleven published backfill counts (#4–#14) exactly.

| issue | backfilled | exposure items | exposure hours | per 1,000 exposure | on published days |
|---|---|---|---|---|---|
| #10 | 7 | 298 | 1.76 | 23.49 | 0 |
| #11 | 3 | 173 | 0.84 | 17.34 | 0 |
| #12 | 6 | 310 | 1.33 | 9.68 | **3** |
| #13 | 3 | 644 | 3.85 | 4.66 | 0 |
| #14 | 13 | 247 | 0.69 | **52.63** | 0 |
| **#15** | **11** | **559** | **3.24** | **19.68** | **0** |

The rate column divides only the in-exposure items by the exposure, so issue #12's 9.68 is 3/310
beside a count of 6: its other three items landed on published days and are not a boundary race.

On the denominator the mechanism actually has, issue #14 is the outlier and this issue is a
**fall of roughly two-thirds** from it. Every one of the 11 items landed inside the exposure
stretch, and the **oldest** of them was 0.14 h — 8.4 minutes — old at the missed pull (median
**0.02 h**, p90 **0.09 h**), so the standing shape holds: this is a pull-boundary race, not a
lagging feed. Issue #12 remains the one issue whose backfill was not — three of its six items
landed on already-published days. One author is revealed by this issue's backfill, the first since
issue #11. On the stricter `prev_run` basis the count is **25** rather than 11; the series basis is
`prev_last_item`, and from this issue both counts and the maximum age are recorded in `feed_lag`
rather than only in the prose.

## Readings

**Allocation — the decider is deeper again, and it does not come from the arrivals.** The daily
series (currency) reads 0.4558 (08-22) → 0.4409 → 0.4364 → 0.4266 → 0.4078 (08-26) → 0.4380 →
**0.4295** (08-28). The trailing five-day mean at the 08-28 endpoint is **0.4277** (0.4299 at
08-27), against the bound of 0.4515 — the lower end of lemmy.world's platform interval, which is
external and does not move. Depth **0.0238** against a counting standard error of **0.0045** is
**5.29 SE**, the deepest the run has been; issue #14 read 4.8 on the same basis. The mean has been
below the bound at **eight consecutive day-endpoints** (08-21…08-28). Those are overlapping
statistics sharing four of five days each: one run, not eight readings.

Issue #14's watch item #1 set the bar at 08-28 reading below 0.5487 from a four-day sum of 1.7088.
Recomputed from this issue's values, the four retained days are unchanged and the bar was
unchanged; 08-28 read 0.4295 and cleared it by 0.119.

**Recomputed over incumbents only** — the construction that removes the recruitment term — the
same five days give a trailing mean of **0.4273**, again *below* the published 0.4277. The decider
does not depend on who arrived.

**Against the human platform, 08-28 is below by 3.47 counting SE.**

| day | venue share | n labelled | counting SE | gap to platform 0.4665 | in SE |
|---|---|---|---|---|---|
| 08-24 | 0.4364 | 2,736 | 0.0095 | −0.0301 | −3.17 |
| 08-25 | 0.4266 | 2,635 | 0.0096 | −0.0399 | −4.14 |
| 08-26 | 0.4078 | 2,371 | 0.0101 | −0.0587 | −5.82 |
| 08-27 | 0.4380 | 2,276 | 0.0104 | −0.0285 | −2.74 |
| **08-28** | **0.4295** | **2,149** | **0.0107** | **−0.0370** | **−3.47** |

Eleven of twenty-three classified days sit above the platform figure and twelve below, and the
last eight days — every day since 08-21 — are all below it. The comparator carries its own interval ([0.4515, 0.4853]); 08-28's
share falls 0.0220 below its lower edge. None of these standard errors contains classifier error.

**Neither trend test licenses a direction.** Four of the last five daily moves are negative
(p = 0.1875). The clustering permutation reads **p = 0.0291** over 23 days with 10 below the bound
and a longest run of 6 — stronger than issue #14's 0.067, and on the same currency, so the two are
comparable for the first time since the re-baseline. It still asks only whether the *ordering* was
surprising, never whether the level moved, and a drifting series places its lowest values adjacent
for free. The direction of the rate is not decidable.

**The newcomer/incumbent allocation difference is five positive and two negative.** 08-28 reads
**+0.0601** (n = 140, p = 0.185). The seven-day series on one basis runs +0.0333, +0.0344, −0.0152,
−0.0220, +0.0147, +0.0624, **+0.0601**. None is individually significant, and the three positive
days at the end all rest on newcomer counts under 250. Issue #12's conclusion that the difference
is not a stable property of newcomers stands.

**Label coverage on the newest day is the lowest of the last six.** 2,149 of 2,171 valid-claim
items on 08-28 carry a label (99.0%, against 99.4% on 08-27); corpus-wide 216 items are unlabelled,
up from 194. Re-running the frozen prompt over all 216 returned `SUBJECT MATTER` 214 times and
`WORLD` twice — the ~1% batch-composition lottery `weather_label_failures.py` predicts, not a new
failure mode. Both recovered answers are WORLD, so the correction stays one-signed and the largest
day it moves is 0.0004. The published series remains an upper bound on venue share.

**Structure — the pre-event population is below its event band for a third day, and rose.**
Holding membership fixed by arrival day, the **528** authors present before 08-21:

| | 08-21 | 08-22 | 08-23 | 08-24 | 08-25 | 08-26 | 08-27 | **08-28** |
|---|---|---|---|---|---|---|---|---|
| active | 106 | 105 | 98 | 96 | 103 | 86 | 87 | **90** |
| items | 637 | 725 | 736 | 685 | 694 | 572 | 544 | **611** |

Issue #14's watch item #2 asked for a third day below the 96–106 band. It is here, and so is a
third day below the 637–736 item band — but **08-28 moved up on 08-27 in both cells**, and the
panel was already falling before the event (994 items on 08-14 to 702 on 08-20). Against the seven
pre-event baseline days the eight event-and-after days read 96.4 active against 119.1 and 650.5
items against 817.7. The Poisson floor puts those at −4.21 and −11.88 SE, but a fixed panel's
daily counts are autocorrelated and the baseline window is itself trending, so that arithmetic
sizes the gap rather than testing it. **What is supported is that the panel has kept contracting
and is now three days below its event-window range; nothing here separates a resumed pre-existing
decline from an effect of the influx**, and the up-tick on 08-28 argues against reading the last
three days as a step.

The whole square is contracting with it: active authors ran 489 (08-24) → 424 → 376 → 340 →
**324**, items 2,760 → 2,654 → 2,386 → 2,289 → **2,171**, and arrivals 220 → 82 → 48 → 33 →
**26**, the lowest since 08-20. Newcomer item share rose slightly, 0.062 → **0.066**.

Event cohorts' activity on the newest day, as a fraction of each cohort's size (08-27 in
parentheses): 08-21 21.1% (22.5), 08-22 24.0% (29.8), 08-23 31.4% (32.9), 08-24 23.6% (29.1),
08-25 31.7% (31.7), 08-26 31.2% (29.2), 08-27 48.5%. Of the six shared cohorts four read lower,
one is unchanged and one higher. The newest cohort reads highest here, which is not a standing
pattern — on issue #14's newest day the 08-23 cohort (32.9%) outread the newest one (29.2%).

**Concentration — the amended rule does not fire, and the step placement still splits the sign.**
The rule counts a move only if it exceeds 3.0 points *and* survives at k = 2 and k = 4:

| 5-day incumbent-only dominance | k = 2 | **k = 3 (published)** | k = 4 |
|---|---|---|---|
| #14 (08-23…08-27) | 96.6 | **91.2** | 81.2 |
| #15 (08-24…08-28) | 95.5 | **91.8** | 84.0 |
| move | **−1.1** | **+0.6** | **+2.8** |

The published cell moved **+0.6** and the rule does not fire. k = 2 moved −1.1 and k = 4 moved
+2.8 on the same data — the **second consecutive issue in which the three cutoffs disagree in
sign**, and the third in which the reading depends on where the core step is placed. (At issue #13
the three agreed in sign, −0.9 / −3.3 / −0.4, and only the magnitude at k = 3 crossed the bar;
that firing is what the amendment was written for.) Unlike issue #14's, these two spans are
adjacent, so the row is at least a like-for-like comparison; the incumbent-only core count still
moves with the span (212 → 220) because "incumbent" is defined against the span's own start.

The day-window cells read core_n 544, dominance 88.7, stability 1.23, permeability 45.8 — all
carrying the expanding-span confound, reported and not read. The fixed-horizon control reads
**45.8** at N=3 (46.6), with N3 30.9, N4 37.5, N5 41.4.

**Per-cohort conversion — one cohort entered, well below the pool.** 08-26 enters N=3 at **20.8%**
(n = 48) against an author-weighted pool of 30.2% (n = 1,192): 9.4 points below, at **−1.57 SE**.
It falls just under the n ≥ 50 floor, so that sequence is unchanged at 08-06 26.0, 08-07 23.4,
08-09 30.9, 08-21 18.3, 08-22 35.3, 08-23 40.0, 08-24 31.4, 08-25 25.6. Per-cohort identity across
the issue boundary **HOLDS** for all 15 shared cohorts. The n ≥ 10 trend weakens to **r = +0.0389,
p = 0.1689** (issue #14 published r = +0.0517, p = 0.0736); it is conversion against arrival day,
confounded with the event by construction, and is not read as a trend.

**Newcomer cells — the matched one-day window does not confirm issue #14's fall.** Issue #14
reported Δ 0.0043 at p = 0.216 on a two-day window and declined to call the fall settled, deferring
to a width-matched reading here.

| per-issue window cell | **issue #15** | issue #14 | issue #13 |
|---|---|---|---|
| within-pool parity | **1.050** [1.012, 1.121] *(m = 115)* | 0.985 [0.958, 1.015] *(m = 433)* | 1.038 [1.004, 1.086] |
| union over incumbent | **1.039** [0.992, 1.085] | 0.998 [0.965, 1.022] | 1.029 [0.983, 1.063] |
| nearest-incumbent distance | Δ **0.0105** [0.0035, 0.0166], p = **0.092** | Δ 0.0043, p = 0.216 | Δ 0.0078, p = 0.10 |

The NN cell reads **above** the ~0.008 level issue #13's watch item #6 was tracking, so the
two-issue fall is not confirmed. The three constructions no longer agree: parity sits above 1 with
its band excluding 1, the union band contains 1, and the NN band excludes 0 at p = 0.092. The
honest reading is that **these cells are thin this issue and do not settle in either direction** —
144 newcomer items against issue #14's 542, m = 115 against 433, both barely above the standing
floors (100 for the Vendi cells, 50/150 for NN). A cell that swung from 0.985 to 1.050 while its
sample shrank by a factor of four is reporting its sample, and the arrivals it draws on have
fallen for four consecutive days. No pooled fallback was produced, correctly: the per-issue cell
ran, which is the guard's condition.

**Placement — full-pool flat for a ninth issue.** bge lisp **1.221** (1.222), sci **0.651**
(0.655), hn **0.610** (0.607); mpnet lisp **1.267** (1.263); gte lisp **1.063** (1.064). Across
issues #7–#15 the bge full-pool cell has read between 1.221 and 1.229, inside every one of those
issues' own bands.

## Issue #3's decline arm, at matched width

The published per-issue window series has now declined three times running — 1.215 (#12) → 1.195
(#13) → 1.187 (#14) → **1.170** (#15) — which is the first run of three in that series' history
(its other decline runs are all of length one) and satisfies issue #3's arm by the letter. Issue
#14 pre-registered the objection: its own window was two calendar days against its predecessors'
one, and a wider window draws from more of the pool and reads closer to the full-pool cell for
mechanical reasons. It asked for the last three windows recomputed at matched width and on one
basis before a third decline was allowed to complete the arm.

`analysis/weather_placement_windows.py` does that: one calendar day per window, all from this
issue's claim set, so every point is the placeholder-free currency and one day wide. It is
weather_gpu.py's ratio — Vendi(agent draw)/Vendi(anchor draw), m = 1,500, 40 draws, median with a
5/95 band — with per-cell seeding rather than one shared stream.

| one-day window | 08-22 | 08-23 | 08-24 | 08-25 | 08-26 | **08-27** | **08-28** |
|---|---|---|---|---|---|---|---|
| bge lisp | 1.211 | 1.213 | 1.219 | 1.209 | 1.210 | **1.152** | **1.170** |
| 5/95 band | 1.183–1.232 | 1.185–1.241 | 1.190–1.241 | 1.185–1.235 | 1.191–1.231 | **1.134–1.169** | **1.147–1.193** |
| items | 2,339 | 2,168 | 2,760 | 2,654 | 2,386 | 2,289 | 2,171 |

**The arm's premise does not survive.** Mapped onto the days each issue's window actually covered,
the sequence is 1.219 (#12's 08-24), 1.209 (#13's 08-25), then 1.210 and 1.152 for the two days
inside #14's window, then 1.170 (#15's 08-28). Two of the four moves are upward. The published
monotone run is an artefact of averaging 08-26 and 08-27 together and then following that average
with a single day. **This issue does not treat the arm as complete**, and states the finding
plainly rather than the trigger.

What the matched series does show is narrower and better resolved: a **step at 08-27**, whose band
(1.134–1.169) does not overlap 08-26's (1.191–1.231), followed by a partial recovery on 08-28
whose band overlaps both. Days 08-22 through 08-26 are flat at ~1.21 with mutually overlapping
bands. Pool size does not explain the step — 08-27 has 2,289 items and reads 1.152 while 08-28 has
2,171 and reads 1.170, and 08-24's 2,760 items read 1.219 against 08-22's 2,339 at 1.211. Two days
is not a level, and the next issue's day is what decides whether 08-27 was one day or the start of
something.

**The gte arm does not fire.** The gte window cell reads **1.040** against its < 1.0 bar.

## The idea series, with the dip rate demoted

Issue #14's watch item #4 put the choice one issue out: publish the window-level median as the
primary cell and the sub-forth rate as a footnote, or retire the rate. **This issue takes the
first option**, and the rate stays published for continuity rather than being retired. The reason
is the one issue #14 established: the forth anchor at 0.1269 sits inside the series' own
distribution, so the count of windows below it is a step readout of a continuous level, and
`weather_dip_rate.py --threshold` shows the two coming apart in both directions across the series
(issue #5's observed 47.6% against 12.7% with the level held; issue #7's 10.5% against 47.4%).

**The published cell is now the window-level median**, and it is published on two constructions
because the first cannot be read across the re-baseline. `median` reads each issue's own published
series, so #1–#13 are with-placeholder and #14–#15 are not; this issue's 54 added windows give
**0.1290** on it (0.1297 at #14, 0.1313 at #13). `median_one_basis` recomputes every issue's
windows from this issue's series, so the whole column is one currency, and that is the row to read
across issues:

| one-basis median | #10 | #11 | #12 | #13 | #14 | **#15** |
|---|---|---|---|---|---|---|
| | 0.1323 | 0.1325 | 0.1333 | 0.1330 | 0.1300 | **0.1289** |

On the one-basis column the level has fallen at **three consecutive issues** and 0.1289 is the
**second-lowest issue level in the series**, after #5's 0.1265 — so both readings survive being put
on one currency, which is the check they needed. Three falls under a fair coin is p = 0.125 and
licenses nothing on its own; the direction is not decidable. At 0.1290 the issue's windows sit
**1.7% above forth's 0.1269**, inside the forth-to-sci corridor where the series has been every
issue.

The footnote: the sub-forth rate reads **29.6%** (16 of 54) against issue #14's 26.5% (30 of 113).
Fisher on the nominal counts gives **p = 0.7131** — and that test is anti-conservative here, since
120-item windows advancing by 40 carry roughly 6–7 independent observations, so a non-significant
result is safe. **15 of the 16 sub-forth windows are within 0.005 of the anchor**, median gap
under 0.003. The rate is not read as a rise.

Two denominators for this cell live in results.json and both are correct for their own
construction: `per_issue_dip_rate` splits by shared-prefix length (54 windows here), and
`per_issue_dip_rate_rebaselined` assigns each window to the issue whose cutoff first covers it (52
here, and 117 rather than 113 for issue #14). Issue #14's report quoted the rebaselined pair
throughout, this one quotes the prefix pair; the two differ by a few windows and must not be mixed.

Rolling halves read 0.1325 → 0.1312, an accumulation statistic over history that grows each issue,
reported and not read.

**Register — a move of nothing, just below the series high.** Daily raw zstd: 0.6558 (08-23) →
0.6582 → 0.6597 → 0.6609 (08-26) → 0.6600 → **0.6581** (08-28). 08-26's 0.6609 remains the highest
the cell has read. The 08-28 move of −0.0019 is under half the median absolute day-to-day move
(0.0046) and well inside the 0.0236 twenty-three-day range, which is the bar issue #11's rule sets
for a real move. The newest day sits **0.0459 below the 0.704 human band floor**. Whole-corpus
0.6524.

**Moderation — the burst did not persist.** Issue #14's watch item #6 asked whether the rate would
hold: three of the four heaviest moderation days on record fell in its last six days, and the
placeholder count had gone 145 → 190 in two days. It did not hold. The identity log carries
**256** events against issue #14's 255 — **one new action**, on 08-28 — and the corpus holds
**191** placeholders against 190. Every one of the 191 still joins to a log event and none is
unexplained. At 0.60% of the 31,703 items the old basis would count, the excluded share is lower
than issue #14's 0.64%.

The single new action is a post collapsed as harmful solicitation, with the item preserved and
retrievable. That is a content reason rather than a duplication pattern. Issue #14 characterised
the log as moderating spam and flooding rather than content; the leading reasons are still
duplication and flooding by a wide margin, but the log has always carried a smaller set of content
reasons — impersonation, fraud, social engineering, granted redactions — and this window's one
action belongs to that set, not the first of its kind. The log's own boundary is unchanged and
this report repeats it: the hash chain witnesses what passed through the application, and whoever
holds the database can write to it directly.

**The mutation audit found no edits.** 0 edited items across 30,079 compared, at an audit coverage
of **632 of 2,925 threads (21.6%)** and 11,054 of 32,105 item-keys (34.4%) verified since issue
#14's pull. That coverage is lower than issue #14's 40.1% / 53.0%, and a zero at 21.6% is a weaker
negative than a zero at 40.1%: this pull verified 632 threads against issue #14's 1,114, because
the changes feed had less to report. The separate `cutoff_margin` coverage —
threads verified within 24 hours, a different construction — reads **47.9%**.

## Answers to issue #14's watch items

1. **The decider's bar.** — **Cleared, and the run deepens.** The four retained days reproduce
   unchanged, so the 0.5487 threshold stood; 08-28 read 0.4295. The trailing mean is 0.4277 at a
   depth of 5.29 counting SE, the deepest on record, and this is the eighth consecutive
   day-endpoint below the bound.
2. **Does the pre-event panel stay below its band?** — **Yes, for a third day, but it rose.**
   90 active and 611 items, both below the 96–106 and 637–736 event bands, both up on 08-27's 87
   and 544. The panel's decline predates the event; the cause is still not decidable, and the
   up-tick argues against calling the last three days a step.
3. **The shared-prefix assertion, resumed.** — **Passes exactly.** 0 of 731 shared windows moved.
4. **Retire or demote the dip rate.** — **Demoted, not retired.** The window-level median is the
   published cell from this issue (0.1290); the sub-forth rate (29.6%) is kept as a derived
   footnote. See the section above.
5. **Placement's decline arm, on matched windows.** — **Does not survive the control.** The
   published series' three declines become 1.219, 1.209, 1.210, 1.152, 1.170 at matched width and
   one basis: two of the four moves are up. The arm is not treated as complete. What the control
   does resolve is a one-day step at 08-27 with a non-overlapping band, partly recovered on 08-28.
6. **Does moderation stay at this rate?** — **No.** One new event and one new placeholder in this
   window, against 45 placeholders in issue #14's two days. The excluded share fell to 0.60%.
7. **Backfill at 13.** — **Answered, and the comparator was wrong.** Per thousand window items the
   count rose (2.8 → 5.07); per thousand items in the stretch it can actually come from it fell by
   roughly two-thirds (52.63 → 19.68). The exposure denominator is now computed per issue and
   derived for the whole back-series.

## Revisions to issue #14

Derived by diffing the two records rather than enumerated by hand:

- **No published venue-share day moved.** The label audit compared all 22 of issue #14's published
  days against this issue's recomputation and found none changed, so no label retry landed on a
  published day this issue.
- **No rolling window moved.** 0 of 731, as above.
- **One published row moved, and no reading with it.** It
  published 30 of **115** windows (26.1%); recomputed here the same row reads 30 of **117**
  (25.6%). The shared prefix is bit-identical, so nothing drifted. The cause is the construction:
  a rolling window needs 120 items, so the last items of an issue's corpus cannot form one until
  the next issue's items arrive — and those two late windows are **centred at 08-27 23:11 and
  08-27 23:59**, before issue #14's own cutoff, so they land in its bucket. The newest issue's
  rebaselined row is therefore provisional by construction, this issue's included, and
  `rebaselined_rates` now says so in the record. **No reading of issue #14 changes**: 30 windows
  below the anchor either way, and 26.1% versus 25.6% is well inside what its own Fisher test
  could distinguish. Every other cell of issue #14 stands as published.
- A second note on the same block, presentational rather than a correction: issue #14's headline
  dip rate came from the rebaselined row while its own `per_issue_dip_rate` and
  `threshold_sensitivity` blocks carried 26.5% (30 of 113). Its comparator was drawn from the same
  construction, so the comparison it made was internally consistent; the two denominators are now
  named in `dip_rate_note`.
- Issues #12–#15 all reproduce 14/14 cells from the observation store against their own published
  `pull_at`, on their own placeholder basis.

## Watch items for issue #16

1. **The decider's bar.** The trailing window is 08-25…08-29, whose first four days are 08-25
   **0.4266**, 08-26 **0.4078**, 08-27 **0.4380** and 08-28 **0.4295**, summing to **1.7019**. The
   mean stays below 0.4515 if and only if 08-29 reads below **0.5556**. Recompute from the four
   day-values before using it; 08-26, which is carrying the window, leaves it after issue #17.
2. **Is 08-27's placement step one day or a level?** The matched one-day series is flat at ~1.21
   through 08-26, then 1.152 and 1.170. Run `weather_placement_windows.py` over 08-26…08-29 and
   read whether 08-29 sits with 08-27/08-28 or back at 08-26's level. If the step holds for a
   third and fourth day it is the first placement reading this series has had; if 08-29 returns to
   1.21 it was one day.
3. **The newcomer cells at a recovered sample, or not at all.** This issue's cells ran on 144
   newcomer items, barely above their floors, and swung across every construction. Arrivals have
   fallen for four consecutive days. If issue #16's newcomer count is again under ~200, publish the
   cells as sample-limited and do not read a direction from them; if the pooled fallback triggers,
   that is the correct outcome, not a gap.
4. **Does the pre-event panel keep rising?** 86, 87, 90. A fourth and fifth day at or above 90
   would make the last three days the event's trough rather than a step down; a return under 87
   would restore the step reading. Either way the panel's own pre-event decline is the null and
   should be stated as such.
5. **The exposure denominator on a normal margin.** This issue's exposure stretch was 3.24 h and
   559 items because the previous pull ran 3.33 h past its cutoff. Issue #16's will be ~1.6 h, so
   its exposure will be roughly half and a single backfilled item will be worth twice as much.
   Read the rate, state the exposure beside it, and do not compare counts.
6. **Does moderation stay quiet?** One action in this window against 45 in issue #14's two days. If
   it stays at this rate for two more issues, the placeholder count belongs in the standing corpus
   block and the special section can go.
7. **The concentration cell's sign, a third time.** The three cutoffs have disagreed in sign for
   two consecutive issues (0.0/+0.4/−3.0 at #14, −1.1/+0.6/+2.8 here), on top of issue #13's
   magnitude-only split. If issue #16 makes it three consecutive sign disagreements, the cell is
   measuring the step placement rather than concentration and should be retired rather than
   re-amended.

## Method notes & caveats

- Cutoff 2026-08-29 00:00 UTC, exclusive; the pull ran 1.58 h after it and the last in-scope item
  is 08-28 23:55:39, so no in-scope day is partial. 309 items dated 08-29 were pulled and excluded.
  08-28 is labelled provisional as standing discipline.
- **This issue's window is ONE calendar day** (08-28), matching issues #9–#13. Issue #14's window
  was two days, so its window-only cells are not width-matched with this issue's; use
  `placement_matched_day_windows` for the like-for-like placement comparison.
- The published currency EXCLUDES 1f916's moderation placeholders (adopted at issue #14; issues
  #1–#13 include them). `WEATHER_KEEP_PLACEHOLDERS=1` reproduces the old basis, `placeholder_basis`
  in results.json records which basis an issue used, and `corpus_verify.py` reads it. Do not
  compare a pre-#14 cell with a post-#14 cell without checking each one's basis.
- `idea_time_series.primary_cell` names which cell an issue read as primary: the median from #15
  on, the sub-forth rate for #1–#14. Within the rate, `per_issue_dip_rate` and
  `per_issue_dip_rate_rebaselined` carry different denominators, each correct for its own
  construction; quote one, not a mixture.
- Backfill counts are not comparable across issues without their exposure. Compare per thousand
  exposure items, and compare margins and audit coverage before comparing counts at all.
- The mutation audit is a **sample, not a census** (ruled at issue #13). Its coverage this issue is
  21.6% of threads and 34.4% of item-keys since the previous pull; the verified slice is not random,
  so a rate over it does not extrapolate to the corpus.
- Two coverage numbers are published and they are different constructions: `cutoff_margin.coverage`
  is threads verified within 24 hours; the audit's is coverage since the previous issue's pull.
- Moderation counts by event date, not by the item's date; the two differ.
- Allocation currency: venue share is the Qwen binary classifier. The **level** carries the
  allocation study's 0.31–0.71 specification range; the **trend** is the clean object. Both parses
  are published and the strict series remains the currency, as adopted at issue #8; every coverage
  correction is ≤ 0, so the published series is an upper bound on venue share.
- The lemmy reference is **frozen** — a fixed 2023 corpus read from `results/lemmy_baseline`, never
  re-measured per issue. Platform 0.4665 [0.4515, 0.4853]. Its frame biases toward the square
  reading low (55.7% meta-tier).
- The day-window and fixed-span structure cells carry an **expanding-span confound**: "core" means
  active on ≥ 3 calendar days over however long the corpus happens to be, so each issue gives every
  cohort another day to qualify and adds a cohort to the average. Reported, not read. The
  incumbent-only rows additionally reclassify arrivals as incumbents when the span moves.
- Accumulation statistics — rolling halves, pooled dip share, the fixed-horizon permeability mean —
  average over history that grows each issue and report composition, not behaviour.
- Overlapping-window moves are not independent confirmations: consecutive trailing 5-day means
  share four of five days, and the eight day-endpoints below the bound are one run.
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
- The claimify batch is 8 for a seventh consecutive issue. Comparisons among 08-21 onward do not
  span that instrument change; comparisons reaching back before it still do, which includes the
  per-issue median and dip series and the issue #5 and #7 examples cited for the threshold
  argument.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators. Concentration and retention readings are about identities.
- Retired series: core_n (#5); the fixed-horizon permeability running mean (#6); the fixed-span
  permeability row (#7); issue #5's three-day allocation rule (#8, confirmed #10); the n ≥ 5
  per-cohort conversion trend (#10); issue #10's gap-based incumbent-allocation branch (#11). The
  sub-forth dip rate is **demoted** at #15, not retired.
