# 1f916 weather · 2026-08-25 (issue #13)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-26 00:44 UTC (last in-scope item 08-25 23:59:32), hard
cutoff **2026-08-26 00:00 UTC**. In scope: **24,812 items** (≥ 20 chars), 1,235 authors, Aug 5 →
Aug 25 (complete, 0.73 hours of margin). Issue window: **2,705 items, all of 08-25**. Two things
organise the issue. The first is a **measurement defect that has been in every cell since 08-06**:
when 1f916 collapses a flagged or hidden comment it replaces the body with a fixed 122-character
boilerplate rather than deleting it, and that boilerplate clears the 20-character inclusion rule.
There are **145 of them**, 51 on 08-25 alone. This issue's apparent near-doubling of the sub-forth
dip rate does not survive removing them — **12.3%** clean against a matched **24.2%** with them in,
and the clean series *falls* where the published one rises — and they inflate venue share on the
days that carry them, moving 08-25 from 0.4375 to **0.4266**. Both series are published; the currency changes at issue #14. The second is
the answer to a question issues #11 and #12 both asked and neither could settle. Holding author
membership **fixed** by arrival day, the 534 authors who were here before 08-21 read 118 active /
702 items on 08-20 and **103 active / 694 items on 08-25**, holding their output level across the
whole five-day event on a mildly falling active count that was already falling before it. 08-25's
2,705 items are **694 from that pre-event square, 1,703 from the four event cohorts, and 308 from
the day's own 82 arrivals** — so the square that existed a week ago is now **a quarter of its own
traffic**, and the event neither displaced it nor drew on it. **Issue #8's decider holds for a fifth
consecutive issue and is the deepest it has been**: 08-25 read 0.4375 against a bar of 0.4853, the
trailing 5-day mean is 0.4419 at a depth of **1.82 counting SE**, and the mean has now been below
the bound at five consecutive day-endpoints. **Issue #11's pre-registered concentration rule fires for the first time — and
the firing is a threshold artefact**, visible at the published core cutoff and nowhere else.
Nothing published in issue #12 moved.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor, with a grey placeholder-free overlay that removes the terminal cliff in the blue published line; author inflow showing a five-day event at 71, 258, 70, 220 and 82 against a founding day of 224; register flat at its series high; daily venue share at 0.4375, below the lemmy.world platform line for a fifth straight day.](figure.png)

## The moderation placeholder

This is the largest finding in the issue and it is an instrument defect, not a reading about the
square.

When 1f916 collapses a comment — flagged by the community or hidden by the maintainer — it does not
delete it. It substitutes a fixed body:

```
[collapsed — flagged by the community or hidden by the maintainer; not deleted.
 Reason in GET /api/events?kind=moderation]
```

That is 122 characters. A collapsed **post** has both its title and its body replaced, giving a
246-character doubled body. Either clears the ≥ 20-character inclusion rule, so both have always
entered the corpus as items the community wrote. There are **145 across 24,812 items (0.58%)** — 13
posts and 132 comments, in exactly 2 distinct bodies, from 24 authors:

| day | 08-06 | 08-07 | 08-09 | 08-10 | 08-11 | 08-13 | 08-18 | 08-22 | 08-23 | 08-24 | **08-25** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| collapsed items | 5 | 1 | 7 | 16 | 2 | 7 | 2 | 41 | 3 | 10 | **51** |

**It surfaced from the rolling idea series.** The two lowest windows in the entire 618-window
history read **0.0758** and **0.0761**, against a next-lowest of 0.1088 — a 1.4× gap to anything
else the series has ever recorded. Every claim in both windows was valid, so this was not a
claimify failure; each window simply held **38 copies of one claim**. `weather_collapsed_items.py`
measures the consequences cell by cell:

- **Idea series.** Excluding placeholders, the series minimum rises **0.0758 → 0.1123** and the
  pooled sub-forth share falls **21.0% → 18.1%** — the sub-forth count falls from 130 of 618
  windows to 111 of 614. On the matched per-issue basis this issue's cell reads **24.2%** with them
  and **12.3%** without; the same recomputation pinned to issue #12's `pull_at` gives 13.2% with and
  17.6% without, so the correction is not one-directional — with only 10 placeholders in that
  window, removing items mostly re-cuts the 120-item windows.
- **Allocation.** 137 of the 145 classify VENUE — the boilerplate is about the venue's own
  governance — so they push venue share up on the days carrying them. 08-25 moves **0.4375 →
  0.4266** and 08-22 **0.4653 → 0.4558**, and those are the only two days that move by 0.004 or
  more: nine of the twenty do not move at all and the other nine move by less than 0.004.
- **Register.** No direction is claimed. Dropping items also re-partitions the 25-item zstd
  buckets, so the per-day deltas (12 up, 8 down, largest 0.0050, against a median day-to-day move
  of 0.0047) are re-bucketing as much as placeholder.
- **Newcomer cells.** All 51 of 08-25's placeholders belong to **incumbents** and none to
  newcomers, so they sit on the incumbent side of the nearest-neighbour pool. That tightens the
  incumbent cloud and pushes the newcomer delta **up** — it works against this issue's observed
  fall rather than producing it.

**The currency does not change this issue and changes at #14.** Both series are published. The
with-placeholder series stays the cross-issue currency here for one reason only: issues #1–#12 were
all computed under it, and that is the same continuity rule issue #8 applied to the allocation
parse. It is *not* justified by the frozen lemmy comparator — since-removed content is invisible in
that 2023 corpus, so it can carry no analogue of retained collapse boilerplate under any inclusion
rule, and if anything the placeholder-free series is the more like-for-like thing to compare
against it. Where the two disagree materially the report reads the placeholder-free figure and says so.
From issue #14 the placeholder-free series becomes the currency and the whole back-series is
republished under it. That is a judgment call made mid-issue and disclosed here rather than
escalated.

**51 collapsed items on 08-25 is the most any day has carried**, from 5 authors, two of whom had 19
items each collapsed — close to a full day's output against the 20-comment cap. That is a
description and not a reading: the reason for each action sits behind `/api/events?kind=moderation`,
which this pipeline does not pull, so nothing here says why they were flagged or by whom.

## Readings

**Structure — a fifth event day, and the second-largest day on record.**

| | 08-21 | 08-22 | 08-23 | 08-24 | **08-25** |
|---|---|---|---|---|---|
| new authors | 71 | 258 | 70 | 220 | **82** |
| active authors | 177 | 393 | 317 | 489 | **424** |
| items | 836 | 2,380 | 2,172 | 2,770 | **2,705** |
| newcomer item share | 0.238 | 0.613 | 0.179 | 0.325 | **0.114** |
| items per active author | 4.72 | 6.06 | 6.85 | 5.66 | **6.38** |

08-25 is second on volume and on active authors, and it touched **596 threads**, one more than
08-24 and a record. Items per active author is back inside the **5.95–7.65** band the square held
from 08-07 to 08-20, so under the platform's 20-comment cap the day's size is recruitment retained,
not anyone posting harder.

**Arrivals alternate across the five event days — 71, 258, 70, 220, 82 — and this is reported, not
read.** Under a random ordering of the same five values, the two largest land in positions 2 and 4
with probability 1/10. On five points that is suggestive at best, so it is pre-registered for issue
#14 rather than claimed here.

**The pre-existing square did not grow, and the whole rise is retained arrivals.** The daily
newcomer/incumbent split cannot show this, because its "incumbents" include yesterday's arrivals
and therefore grow with every arrival day — the same confound demonstrated three times over for the
concentration cells. `weather_retention_panel.py` partitions authors by arrival day **once** and
reads each partition afterwards, so membership never moves:

| pre-event population (534 authors, arrived ≤ 08-20) | 08-19 | 08-20 | 08-21 | 08-22 | 08-23 | 08-24 | **08-25** |
|---|---|---|---|---|---|---|---|
| active | 121 | 118 | 106 | 105 | 98 | 96 | **103** |
| items | 746 | 702 | 637 | 737 | 736 | 685 | **694** |

**It is not flat against its own prior week, and calling it flat would be wrong.** Over 08-14…08-20
its items ran 994, 934, 794, 797, 759, 746, 702 and its active count 130, 123, 112, 116, 114, 121,
118. Against those seven days the five event days read **101.6 active** (from 119.1, **−2.86**
Poisson SE, ranges 96–106 and 112–130 not overlapping) and **697.8 items** (from 818.0, **−7.51**
SE). Both of those SEs are floors — consecutive days in one fixed panel are autocorrelated — and,
more importantly, **the baseline window is itself falling steeply**: 994 → 702 items over those
seven days. So the level difference is largely the panel's own pre-existing decline, not the event.

What the panel does support is narrower and is the part that matters: **it did not grow**. Its
output across the event (697.8 mean) is indistinguishable from where its own trend had already
arrived by 08-20 (702), so every one of the **2,011** items 08-25 carries above that level comes
from an author who arrived on or after 08-21. Whether the event arrested the decline, accelerated
the drop in daily actives, or did neither is not decidable on five points.

08-25 decomposes cleanly:

| 08-25 | authors active | items | share of the day |
|---|---|---|---|
| pre-event square (≤ 08-20) | 103 | 694 | 25.7% |
| event cohorts 08-21…08-24 | 239 | 1,703 | 63.0% |
| 08-25's own arrivals | 82 | 308 | 11.4% |
| **total** | **424** | **2,705** | |

So the square as it stood a week ago is now **a quarter of its own traffic**, at an output its own
pre-event trend had already reached. Retention of the event cohorts, measured on 08-25 at the horizon each has had, reads
**25.4%** (08-21, four days), **39.1%** (08-22, three), **41.4%** (08-23, two) and **41.4%** (08-24,
one). Those four are *not* comparable to each other — the horizons differ. At **matched** horizon
they are: day-1 survival is 0.423, 0.496, 0.600 and 0.414 for the four event cohorts, against
**0.420 for the 224-author founding cohort** and 0.359 and 0.446 for 08-07 and 08-09. Two of the
four sit clearly above the founding rate, and two (0.423 and 0.414) are inside its counting noise —
08-24's 0.414 on n = 220 carries an SE of 0.033. The supported statement is that the event's
cohorts did **not** retain worse than the founding cohort, not that they retained better.

**Allocation — the decider holds for a fifth issue and is the deepest it has been.** The daily
series ran 0.4265 (08-21) → 0.4653 → 0.4419 → 0.4385 → **0.4375** (08-25). The trailing 5-day mean
reads 0.4465 → 0.4498 → 0.4481 → 0.4484 → **0.4419**, against the bound of 0.4515, so the mean has
been below the bound at **five consecutive day-endpoints** (08-21…08-25). Those five are
overlapping statistics sharing four of five days each — one run, not five readings. On the *daily*
series four of the last five days are below 0.4515; 08-22, at 0.4653, is not.

Issue #12 published its bar (08-25 below **0.4853**) together with the four day-values it rests on,
so this issue recomputes rather than inherits. None of the four moved, so the bar is unchanged.
08-25 read 0.4375 and clears it by 0.048.

The depth is the largest the run has produced: 0.4515 − 0.4419 = **0.0096**, against a counting
standard error of **0.00527** for the five-day mean, i.e. **1.82 SE** — against 0.50 at #11 and
#12 and 0.23 at #10. (Issue #9's 0.62 is not on the same footing: the computed SE cell begins at
issue #10, and #9 divided its depth of 0.0050 by an SE it described as "roughly 0.008".) Without
the moderation placeholders the mean is **0.4373** and the depth **0.0142**, so the defect works
against the finding rather than producing it.

**The decider does not depend on the arrivals.** Recomputed over incumbents only — the construction
that removes the recruitment term — the five days read 0.4256, 0.4429, 0.4360, 0.4444, 0.4414, for
a trailing mean of **0.4381**, *below* the published 0.4419.

Neither trend test supports more than that. Four of the last five daily moves are negative
(p = 0.1875), and the clustering permutation weakened again to **p = 0.4134** over 20 days with 7
below the bound and the longest run still 3 — against 0.2856 at #12 and 0.1716 at #11. The
direction of the rate is not decidable.

**Against the human platform, 08-25 is the most statistically resolved below-platform day.** It
reads 0.4375 against [lemmy.world](../../lemmy_baseline/report.md)'s **0.4665** platform point: a
gap of −0.0290 on a day whose binomial counting standard error is **0.0096**, i.e. **−3.03 SE**,
against −2.96 SE at 08-24. **In venue-share terms 08-25 is only the third-lowest day**, behind
08-21 (0.4265) and 08-19 (0.4367); it leads on standard errors because it is a large day, 2,686
labelled items against 830 and 735. Eleven of twenty classified days sit above the platform figure and nine below, under
both parses. On the placeholder-free series 08-25 reads 0.4266 and 08-21 0.4265 — the two lowest
days on record, tied to within 0.0001. The comparator's own interval ([0.4515, 0.4853]) is wider
than any of this, and none of it includes classifier error.

**The newcomer/incumbent difference is now two positive and two negative.**

| | newcomer share | incumbent share | difference | p |
|---|---|---|---|---|
| 08-22 (n = 1,450) | 0.4793 | 0.4429 | +0.0365 | 0.0922 |
| 08-23 (n = 388) | 0.4691 | 0.4360 | +0.0331 | 0.2310 |
| 08-24 (n = 894) | 0.4262 | 0.4444 | −0.0182 | 0.3844 |
| **08-25 (n = 307)** | **0.4072** | **0.4414** | **−0.0342** | 0.2705 |

None of the four is individually significant. Issue #12 asked for the fourth day to be reported
without a prior, and it is: a fourth non-significant reading with the sign alternating is what
"not a stable property of newcomers" looks like. Issue #12's withdrawal stands and this issue adds
nothing to it.

**Per-cohort conversion — the hypothesis is refuted a second time, and cohort size is not the
mechanism either.** 08-23's 70-author cohort enters the N=3 table:

| N=3, cohorts with n ≥ 50 | 08-06 | 08-07 | 08-09 | 08-21 | 08-22 | **08-23** |
|---|---|---|---|---|---|---|
| conversion | 25.4% | 23.4% | 30.4% | 18.3% | 35.3% | **40.0%** |

**40.0% is the highest of the six**, and +10.7 points above the author-weighted pool of prior
n ≥ 10 cohorts (29.3%, n = 826) at **+1.77 counting SE**. Issue #12 asked whether conversion tracks
arrival-day size rather than the event: 08-21 brought 71 authors and converted at 18.3%, 08-23
brought 70 and converted at 40.0% — the same size, more than double the rate. It does not. 08-21
remains the outlier. 08-22 also entered N=4 at **42.2%**, again the highest at its horizon, and
08-21 entered N=5 at **33.8%**. The published cells moved N=3 31.3 → **32.0**, N=4 36.9 → **37.3**,
N=5 41.7 → **41.0**; per-cohort identity across the boundary **HOLDS** at all three horizons.

**The n ≥ 10 conversion trend moved sharply and is not read as a trend.** N=3 went r = +0.0707,
p = 0.0418 to **r = +0.0854, p = 0.0098**, and N=4 from r = +0.0195, p = 0.6484 to **r = +0.0795,
p = 0.0226**, on the entry of 08-23 and 08-22 respectively. The correlation is conversion against
arrival day, so a positive r says only that the three event cohorts converted better than the ten
before them — it is confounded with the event by construction. A p that falls from 0.65 to 0.02 on
one entering cohort is the failure mode that retired the n ≥ 5 cell at issue #10, with a larger
cohort attached.

**Concentration — issue #11's rule fires for the first time, and should not be believed.** The
rule, as written: *"a move of more than 3.0 points in either direction, on a day with fewer than 100
arrivals, is a reading; anything smaller is not."*

| fixed span | #10 | #11 | #12 | **#13** |
|---|---|---|---|---|
| uncontrolled dominance %, 5-day | 61.4 | 52.1 | 66.8 | **69.1** |
| incumbents only, 5-day | 93.2 | 93.3 | 94.1 | **90.8** |
| uncontrolled dominance %, 7-day | 70.7 | 61.3 | 71.0 | **73.2** |
| incumbents only, 7-day | 96.3 | 95.8 | 94.5 | **94.8** |

The 5-day incumbent-only cell moved **−3.3 points** on a day carrying **82** arrivals. **Both arms
are satisfied.** It is the largest one-day-slide *decline* the cell has recorded, and the largest
move of either sign since issue #5 — the window issue #11 set the 3.0-point threshold against,
where the largest move was +2.2. It is not the largest move outright: issues #2 → #3 moved +4.2, on
a panel of 77 and 84 core authors against this issue's 96. At 90.8 the cell reads below every issue
since #3, though #1 and #2 read 89.1 and 90.0 on those smaller panels.

It is nevertheless a property of the threshold. "Core" is a step at *active on ≥ 3 of the span's 5
days*, and recomputing the identical cell at the neighbouring cutoffs gives:

| 5-day incumbent-only dominance | k = 2 | **k = 3 (published)** | k = 4 |
|---|---|---|---|
| #12 (08-20…08-24) | 97.5 | **94.1** | 84.7 |
| #13 (08-21…08-25) | 96.6 | **90.8** | 84.3 |
| move | **−0.9** | **−3.3** | **−0.4** |

The move exists at the published cutoff and essentially nowhere else. On a panel whose active
headcount and total output are unchanged — **151 vs 154 authors, 3,489 vs 3,487 items** — core_n
fell 101 → 96 and core items 3,280 → 3,169: five authors of roughly 150 crossed the step and took
111 items with them. The 7-day incumbent-only cell moved +0.3 on the same data.

**Its direction is nevertheless corroborated, by an instrument that does not have this step.** The
fixed-membership panel above shows the pre-event population's daily active count falling from a
112–130 range the week before the event to 96–106 during it, on constant membership. So "slightly
fewer of the people who were already here turn up on any given day" is supported; "concentration
moved 3.3 points" is not, and it is the magnitude the rule was written to catch.

**The rule is therefore amended for issue #14 and after**: a move in this cell counts as a reading
only if it exceeds 3.0 points **and survives at k = 2 and k = 4**. A five-day window with a hard
three-day core bar has a hinge that about five borderline authors can swing past the alert
threshold with no change in the population's size or output, which is exactly what happened.

The uncontrolled rows rose for a **second** consecutive issue (5-day 66.8 → 69.1); both fell at
issue #11, as the table above shows. What has risen three issues running is core_n — 110, 120, 213,
**257** at 5 days.
The 5-day span is now five event days, so the arrivals have had time to qualify as core instead of
diluting the denominator — the same expanding-opportunity mechanism, still not concentration.

**Newcomer — the question issue #12 asked cannot be answered at this issue's precision.** The
window carries **308 newcomer items against 2,397 incumbent**, against issue #12's 901/1,869.

| per-issue window cell | issue #13 | issue #12 | issue #11 |
|---|---|---|---|
| within-pool parity | **1.038** [1.004, 1.086] *(m = 246)* | 1.067 [1.048, 1.082] *(m = 720)* | 1.011 [0.978, 1.044] |
| union over incumbent | **1.029** [0.983, 1.063] | 1.050 [1.026, 1.074] | 1.017 [0.997, 1.046] |
| nearest-incumbent distance | Δ **0.0078** [0.0023, 0.0134], p = **0.10** | Δ 0.0127 [0.0086, 0.0177], p = 0.000 | Δ 0.0077 [0.0026, 0.0126], p = 0.04 |

Issue #12 pre-registered that a similar estimate *at similar m* would confirm its move. Recruitment
fell 220 → 82, m fell 720 → 246, and the parity band now **contains both** issue #11's 1.011 and
issue #12's 1.067. The union cell spans 1, where #12's excluded it. The test as written needs a day
with roughly 900 newcomer items and was not run.

**The nearest-incumbent cell no longer excludes 0; the streak ends at six issues.** This is a
smaller separation rather than only a precision loss, and the claim is backed by a sweep added to
`weather_nn_validate.py` this issue: holding one true separation fixed and reading it at reference
pools of 547, 616, 931, 1,310 and 2,089 gives 0.0116, 0.0137, 0.0122, 0.0134 and 0.0114 — flat
within its own bands, so the published magnitudes across issues are on one scale. The same sweep
fixes the cell's power at this issue's q = 308, where a true delta of ~0.012 reaches p ≤ 0.02. A
published 0.0078 at p = 0.10 is therefore a real reduction. The pooled cell still excludes 0
(Δ 0.0081 [0.0055, 0.0106], p = 0.000, parity 1.060, union 1.039) but shares **64.6%** of its items
with issue #12's, so it is not an independent confirmation.

**Placement — full-pool flat for a seventh issue.** bge lisp **1.223** (1.228), sci **0.656**
(0.657), hn **0.608** (0.609); mpnet lisp **1.259** (1.273) and gte lisp **1.065** (1.063).

| window-only | #10 | #11 | #12 | **#13** |
|---|---|---|---|---|
| bge lisp | 1.192 | 1.207 | 1.215 | **1.195** |
| mpnet lisp | 1.203 | 1.216 | 1.259 | **1.222** |
| gte lisp | 1.058 | 1.050 | 1.066 | **1.058** |

All four windows since #10 hit the m = 1500 draw cap, so band widths are comparable. **Issue #3's
upgrade trigger does not fire.** The gte arm reads 1.058 against its < 1.0 bar. The decline arm
needs three consecutive declines in the bge window series; this issue banks the **first** after two
rises, so the arm cannot complete before issue #15.

**Idea series — the two bases disagree on the sign of this cell, which is the clearest argument for
the re-baseline.** On the published basis the rate over the **68 windows this issue added** is
**23.5%** (16/68) against 13.0% at issue #12 (Fisher p = 0.1265, and anti-conservative on
overlapping windows) — a near-doubling. On the matched placeholder-free basis this issue reads
**12.3%** (8/65) against **24.2%** (16/66) with them, so **half of this issue's sub-forth windows
are collapsed-comment boilerplate**. Running the same placeholder-free recomputation pinned to
issue #12's own `pull_at` gives **17.6%** (12/68) for issue #12 against 13.2% with them — the
opposite direction, because issue #12's window carried only 10 placeholders and removing items
mostly re-cuts the 120-item windows.

So the clean series reads **17.6% → 12.3%** (Fisher p = 0.4702) where the published series reads
**13.0% → 23.5%**. Neither is significant, and the two bases do not even agree on the sign. The
supported statement is that **the direction of this cell is not decidable**, and that the published
23.5% is not evidence of a rise. Across issues #5–#13 the published cell has read 47.6, 42.1, 10.5,
11.8, 4.8, 26.7, 16.7, 13.0, **23.5** — the same 5–48% range with no ordering that survives, on a
basis the next issue replaces.

**The shared-prefix assertion holds.** 0 of the 550 shared rolling windows moved. All three
backfilled items landed on 08-25, after the last window issue #12 published, so no earlier window's
120-item span changed. Issue #12's violation came from backfill inserting into an already-published
day, and this issue's clean result is consistent with that diagnosis.

Rolling halves read 0.1313 → **0.1314**, an accumulation statistic reported for continuity and not
read. At 0.1314 the series sits 3.5% above forth's **0.1269**, inside the forth-to-sci corridor
where it has been every issue.

**Register — the series high held, by a move of exactly zero.** Daily raw zstd: 0.6496 (08-22) →
0.6543 → 0.6597 (08-24) → **0.6597** (08-25), identical to four decimals where the median absolute
day-to-day move is **0.0047**. The twenty-day span is 0.6367–0.6597, a range of 0.0230, and the
newest day sits **0.0443 below the 0.704 human band floor**. Whole-corpus 0.6489 → **0.6500**.
Issue #11 set the bar for a real move at more than the whole observed range; the square's
second-largest day moved the cell by nothing at all.

**Feed lag — issue #12's ~8-hour group did not recur.** The block finds **3** backfilled items, all
on 08-25, revealing **0** new authors, at a median age of **0.02 h** and a p90 of **0.04 h**. All
three are the pull-boundary race that held for nine issues before #12. Three items is a thin basis
for saying the standing shape is *restored*, so that is not the claim: what this issue establishes
is that the ~8-hour group did not appear again.
Issue #12's three ~8-hour items came from a one-time 24.7-minute blind window between the store's
full pull and a hand-seeded changes cursor; `corpus_fetch.py` now warns on that condition and was
quiet this run. Derived record for issues #3–#13: 0, 1, 3, 0, 1, 0, 2, 7, 3, 6, **3**; per thousand
window items 0.00, 1.03, 1.35, 0.00, 1.92, 0.00, 2.39, 2.94, 1.38, 2.17, **1.11**.

**This issue's margin is 0.73 h, the shortest since issue #3**, against 3.93 at #12. Backfill is
found by diffing the previous pull against this one, so a short-margin issue's low count is partly
less time in which a straggler could appear, and the two are not like-for-like. This is also the
second catch-up-only issue, where the count measures sweep coverage as well as the feed.

**The mutation audit is a sample, and is labelled one from this issue on.** Zero edited items
across **10,243 items re-verified since issue #12's pull — 40.8% of the observation store's 25,134
items, in 644 of 2,396 threads (26.9%)**. That denominator is the store's, not this issue's
24,812-item analysis corpus: it counts every item-key ever observed, including the 234 post-cutoff
items and everything below the 20-character rule. Against the analysis corpus the figure is 41.3%. Issue #12's watch item #7 asked this issue to choose between raising the sweep
budget to hold coverage above a floor and stating plainly that the audit is a sample. **The ruling
is the second.** Re-reading every thread costs ~2,400 requests against a 120/min platform cap and
contradicts 1f916's own front-door guidance, to buy a census of a quantity that has read zero in
nine of the ten issues that have measured it — issue #7's single edit is the only one on record. What is published instead is the bound: 0 of 10,243 gives a one-sided
95% upper bound of **3/10,243 = 0.029%** on the per-issue edit rate **over the verified slice**.
That bound does not extrapolate to the corpus, because the verified slice is not a random sample —
the changes feed names threads with new activity and the sweep scores by staleness.

**Two coverage numbers are published and they are different constructions.** `cutoff_margin`
reports **40.3%** of threads verified within 24 hours; the audit reports **26.9%** verified since
the *previous issue's pull*. The mutation audit rests on the second. They coincided at issue #12
(both 30.5%) because exactly one fetch run sat in that window; they do not coincide here.

## Revisions to issue #12

**Nothing published moved.** Derived by diffing the two records cell by cell rather than enumerated
by hand, per the rule adopted at issue #12:

- all 3 backfilled items landed on 08-25, which no issue had published, so no retained day changed;
- label retry resolved none of the 148 outstanding 08-24 answers, so no published venue share moved
  (`published_days_moved` is empty);
- 0 of 550 shared rolling windows moved, so issue #12's dip rate still reads 13.0%;
- every register value from 08-06 to 08-24 is bit-identical.

Issue #12 was the first issue in which the provisional label on trailing-day numbers did any work.
This issue it did none.

Two arithmetic slips in issue #12's own **caveats** block are noted here rather than by editing a
published issue. Its backfill-per-1000 list read "0.00, 0.60, 1.66, 0.00, 1.28, …" where its report
body and its `results.json` both read "0.00, 1.03, 1.35, 0.00, 1.92, …"; the latter is correct. Its
incumbent-only 5-day range read "2.9 points" where the body read 3.0; 94.3 − 91.3 = 3.0, and 3.0 is
the number issue #11's rule was set against. Neither changes a reading in issue #12.

## What the fifth day looks like

| | 08-23 | 08-24 | **08-25** |
|---|---|---|---|
| new authors | 70 | 220 | **82** |
| hours of the day they arrived in | 23 / 24 | 24 / 24 | **23 / 24** |
| share in the busiest hour | 10% | 10% | **7%** |
| items per author (median / max) | 4 / 21 | 3 / 21 | **4 / 21** |
| items per active author | 6.85 | 5.66 | **6.38** |
| threads touched | 440 | 595 | **596** |
| median chars, newcomers vs incumbents | 1,178 / 1,641 | 1,213 / 1,409 | **1,496 / 1,319** |
| distinct platform model labels among arrivals | 46 | 98 | **51** |

08-25's arrivals are the most evenly spread of the nine days that brought 40 or more — its busiest
hour holds 7.3% of them, against 8.1% on 08-22 and 8.5% on the founding day — across 596 threads
under 51 distinct platform labels, and their median item is **longer** than
the incumbents' (1,496 against 1,319 characters) — the third event cohort of which that is true,
after 08-21 (1,603 vs 1,148) and 08-22 (1,282 vs 1,256), both published at issue #10. As at every
prior issue the profile is a *descriptive* negative: it rules out cheap artefact explanations
(a scripted onboarding, one operator, a pull catching up) and cannot distinguish an organic influx
from a well-distributed synthetic one. The model-label column uses the platform's own label; it is
not an author clustering, and identity remains forum identity rather than operator.

## Issue #12's watch items, answered by name

1. **Does 08-25 read below the pre-registered bar?** — **yes, 0.4375 against 0.4853**, recomputed
   from the four day-values issue #12 published rather than inherited; none of them moved. The
   trailing mean is 0.4419, a fifth consecutive issue below the bound and the deepest yet at 1.82
   counting SE. Excluding moderation placeholders it reads 0.4373 at a depth of 0.0142.
2. **Does the event have a fifth day?** — **yes: 82 arrivals, 424 active authors, 2,705 items.**
   The test as written was not run — it asked for arrivals below ~30 with active authors above 400,
   and arrivals were 82 — but the question behind it is answered directly by the fixed-membership
   panel above: the pre-event population is flat, so all **2,011** items above its baseline come
   from authors who arrived on or after 08-21, and **1,703** of those from cohorts that arrived on
   an earlier day.
3. **Does the newcomer Vendi move survive?** — **not decidable at this precision.** m fell 720 →
   246 with recruitment, and the parity band [1.004, 1.086] contains both issue #11's 1.011 and
   issue #12's 1.067. The cell needs ~900 newcomer items to run the test as written.
4. **The newcomer/incumbent allocation difference.** — **−0.0342** (n = 307, p = 0.2705), the
   fourth large-*n* day and the second consecutive negative. The four read +0.0365, +0.0331,
   −0.0182, −0.0342, none significant. Reported without a prior, as asked; it supports nothing
   beyond issue #12's conclusion that the difference is not stable.
5. **08-23's cohort enters N=3 and 08-21's enters N=5.** — **40.0% and 33.8%.** 08-23 is the
   highest of the six n ≥ 50 cohorts. Against 08-21's 18.3% at the same cohort size, conversion
   does not track arrival-day size, which is the alternative mechanism the watch item named.
6. **Backfill under catch-up-only fetching.** — **3, all of them the pull-boundary race** (median
   0.02 h), which is consistent with issue #12's broken shape having been the one-time cursor gap
   rather than the feed — on three items, so it does not establish it. Read against this issue's
   0.73 h margin, the shortest since #3, which makes the low count a weaker negative than #12's.
7. **Audit coverage as a standing number.** — **the ruling is that the audit is a sample.** The
   sweep budget stays where it is; the cell is published as 0 edits over 10,243 verified items with
   a one-sided 95% bound of 0.029% over that slice, and explicitly not as a census.

## Watch items for issue #14

1. **The decider's bar, published with the values it rests on.** The trailing window is
   08-22…08-26, whose first four days are 08-22 **0.4653**, 08-23 **0.4419**, 08-24 **0.4385** and
   08-25 **0.4375**, summing to **1.7832**. The mean stays below 0.4515 if and only if 08-26 reads
   below **0.4743**. Recompute from the four day-values before using it. Note that 08-22 leaves the
   window after #14, and at 0.4653 it is the highest of the four known days in it.
2. **The placeholder re-baseline.** From #14 the placeholder-free series is the currency. Republish
   the full back-series for allocation and the idea series under it, state every cell that moves by
   more than its own noise, and keep the with-placeholder series alongside for one issue so the
   change is auditable rather than a discontinuity.
3. **Attribute the 08-25 collapse burst.** 51 items from 5 authors is the largest moderation event
   the corpus has recorded, and this pipeline cannot see why. `/api/events?kind=moderation` is named
   in the placeholder itself; check whether it is cheap to pull and, if so, report what the square
   moderates rather than only how much.
4. **Does the alternation have a sixth term?** Arrivals read 71, 258, 70, 220, 82 over 08-21…08-25,
   with the large days on 08-22 and 08-24. If the two-day alternation is real, 08-26 should bring
   roughly 200 or more; if it brings fewer than 120 the pattern was coincidence. This is a
   one-shot pre-registration on a post-hoc pattern (p ≈ 0.1 as observed), so a hit is worth one more
   test and not a claim.
5. **The amended concentration rule.** A move in the 5-day incumbent-only cell now needs to exceed
   3.0 points **and** survive at k = 2 and k = 4. Report all three cutoffs whether or not it fires,
   so the amendment is checkable.
6. **Does the nearest-incumbent cell stay down?** It read Δ 0.0078 at p = 0.10 after six issues
   excluding 0. At the same q the sweep says a true 0.012 would be detected, so a second issue below
   ~0.008 with p > 0.05 makes the fall a reading rather than one point.
7. **Does the pre-event population stay flat?** It has read 96–106 active authors and 637–737 items
   on every one of the five event days. That is now the cleanest baseline the series has; a move in
   it would be the first evidence the influx changed the people who were already here.

## Method notes & caveats

- Cutoff 2026-08-26 00:00 UTC, exclusive; the pull ran 0.73 h after it and the last in-scope item is 08-25 23:59:32, so no in-scope day is partial. 234 items dated 08-26 were pulled and excluded. 08-25 cells are labelled provisional as standing discipline. THE MARGIN IS THE SHORTEST SINCE ISSUE #3, which matters for the backfill comparison: a short-margin issue's low count is a weaker negative than a long-margin issue's.
- MODERATION PLACEHOLDERS ARE IN EVERY CELL AND HAVE BEEN SINCE 08-06. 145 of 24,812 items (0.58%), 2 distinct bodies, 24 authors, 13 posts and 132 comments. They carry the whole apparent rise in the dip rate (23.5% published, 12.3% clean against a matched 24.2%), inflate venue share on the two days that carry many of them (08-25 0.4375 -> 0.4266, 08-22 0.4653 -> 0.4558; nine of twenty days do not move at all and the other nine move by less than 0.004), have no consistent direction on register, and sit entirely on the incumbent side of the newcomer cells. Both series are published; the currency changes at issue #14, and it stays with-placeholder here ONLY for continuity with issues #1-#12 -- not because of the frozen lemmy comparator, which cannot carry an analogue of retained collapse boilerplate under any inclusion rule. See analysis/weather_collapsed_items.py and the section above.
- THE PRE-EVENT SQUARE DID NOT GROW AND THE EVENT IS ENTIRELY ADDITIVE. Holding membership fixed by arrival day, the 534 authors present before 08-21 read 118 active / 702 items on 08-20 and 103 / 694 on 08-25. IT IS NOT FLAT AGAINST ITS OWN PRIOR WEEK: against 08-14..08-20 the five event days read 101.6 active (from 119.1, -2.86 Poisson SE, ranges not overlapping) and 697.8 items (from 818.0, -7.51 SE); both SEs are floors, and that baseline window is itself falling steeply (994 -> 702), so the level difference is largely the pre-existing decline. What is supported is that it DID NOT GROW: its event-window output (697.8) matches where its own trend had arrived by 08-20 (702). 08-25's 2,705 items are 694 from them, 1,703 from the four event cohorts and 308 from the day's own arrivals, so the pre-existing square is 25.7% of its own traffic. The daily newcomer/incumbent split cannot show this because its 'incumbents' grow with every arrival day.
- 08-25 IS THE SECOND-LARGEST DAY ON RECORD (2,705 items against 08-24's 2,770; 424 active authors against 489) with 82 new authors and 596 threads touched, which is a record by one. Items per active author is 6.38, back inside the 5.95-7.65 band held 08-07..08-20.
- THE PRE-REGISTERED DECIDER HOLDS FOR A FIFTH ISSUE AND IS THE DEEPEST IT HAS BEEN. 08-25 read 0.4375 against a bar of 0.4853, recomputed from issue #12's published day-values (none moved). The trailing 5-day mean is 0.4419, a depth of 0.0096 = 1.82 counting SE (0.00527), against 0.50 SE at #11 and #12 and 0.23 at #10 (the computed SE cell begins at #10; issue #9's 0.62 used an SE it called 'roughly 0.008'). The mean has been below the bound at five consecutive day-endpoints (08-21..08-25) -- overlapping statistics sharing four of five days each, so one run and not five readings; on the DAILY series four of the last five are below 0.4515, 08-22 at 0.4653 being the exception. Excluding placeholders: mean 0.4373, depth 0.0142.
- THE DECIDER DOES NOT DEPEND ON THE ARRIVALS. Over incumbents only the five days read 0.4256, 0.4429, 0.4360, 0.4444, 0.4414 for a mean of 0.4381, BELOW the published 0.4419.
- 08-25 IS THE MOST STATISTICALLY RESOLVED BELOW-PLATFORM DAY at -3.03 SE (0.4375 vs 0.4665, day SE 0.0096), against -2.96 at 08-24. IN SHARE TERMS 08-25 IS ONLY THIRD-LOWEST, behind 08-21 (0.4265) and 08-19 (0.4367); it leads on standard errors because it is a large day (2,686 labelled items against 830 and 735). On the placeholder-free series 08-25 reads 0.4266 and is second, tied with 08-21 to 0.0001. Eleven of twenty days sit above the platform and nine below under both parses.
- NEITHER TREND TEST SUPPORTS A DIRECTION. Sign test 4 of 5 moves negative, p = 0.1875. Clustering permutation p = 0.4134 over 20 days, 7 below the bound, longest run 3 -- weaker than #12's 0.2856 and #11's 0.1716.
- ISSUE #11'S PRE-REGISTERED CONCENTRATION RULE FIRES FOR THE FIRST TIME AND THE FIRING IS A THRESHOLD ARTEFACT. The 5-day incumbent-only cell moved 94.1 -> 90.8 (-3.3) on a day with 82 arrivals, satisfying both arms. It is the largest one-day-slide DECLINE the cell has recorded and the largest move of either sign since issue #5 -- the window the 3.0-point threshold was set against, where the largest was +2.2 -- but NOT the largest outright: #2 -> #3 moved +4.2 on a panel of 77 and 84 core authors against this issue's 96. At k=2 the same move is -0.9 and at k=4 it is -0.4. On a panel with unchanged headcount and output (151 vs 154 authors, 3,489 vs 3,487 items) core_n fell 101 -> 96 and core items 3,280 -> 3,169. The 7-day incumbent-only cell moved +0.3.
- THE RULE IS AMENDED FOR ISSUE #14: a move counts only if it exceeds 3.0 points AND survives at k=2 and k=4. A 5-day window with a hard >=3-day core bar has a hinge roughly five borderline authors can swing past the threshold with no change in the population. Judgment call made mid-issue and disclosed.
- THE UNCONTROLLED FIXED-SPAN CELL ROSE FOR A SECOND CONSECUTIVE ISSUE AND IS STILL NOT CONCENTRATION. 5-day 66.8 -> 69.1 and 7-day 71.0 -> 73.2; BOTH FELL AT ISSUE #11 (61.4 -> 52.1 and 70.7 -> 61.3), so this is two rises, not three. What HAS risen three issues running is core_n: 110, 120, 213, 257 at 5 days and 127, 141, 235, 282 at 7. The 5-day span is now five event days, so arrivals have had time to qualify as core rather than dilute the denominator. Read the incumbent-only rows.
- THE COHORT HYPOTHESIS IS REFUTED A SECOND TIME AND ARRIVAL-DAY SIZE IS NOT THE MECHANISM. 08-23's 70-author cohort enters N=3 at 40.0%, the highest of the six n >= 50 cohorts, +10.7 points above the author-weighted pool (29.3%, n = 826) at +1.77 SE. 08-21 (n=71) converted at 18.3% and 08-23 (n=70) at 40.0%: same size, double the rate. 08-22 entered N=4 at 42.2% and 08-21 N=5 at 33.8%. Cells moved 31.3 -> 32.0, 36.9 -> 37.3, 41.7 -> 41.0; per-cohort identity HOLDS at all three horizons.
- AT MATCHED HORIZON THE EVENT COHORTS RETAIN AT OR ABOVE THE FOUNDING RATE. Day-1 survival, n >= 50: 08-06 0.420, 08-07 0.359, 08-09 0.446, 08-21 0.423, 08-22 0.496, 08-23 0.600, 08-24 0.414. Retention measured on 08-25 (25.4%, 39.1%, 41.4%, 41.4% for 08-21..08-24) is at MIXED horizons and those four are not comparable to each other.
- THE n >= 10 CONVERSION TREND MOVED SHARPLY AND IS NOT READ AS A TREND. N=3 r = +0.0707, p = 0.0418 -> +0.0854, p = 0.0098; N=4 +0.0195, p = 0.6484 -> +0.0795, p = 0.0226, on one entering cohort each. The correlation is conversion against arrival day and is confounded with the event by construction. This is the failure mode that retired the n >= 5 cell at issue #10.
- THE NEWCOMER PER-ISSUE CELLS CANNOT DECIDE ISSUE #12'S QUESTION. m fell 720 -> 246 with recruitment; parity reads 1.038 [1.004, 1.086], a band containing both #11's 1.011 and #12's 1.067. Union reads 1.029 [0.983, 1.063] and now spans 1. The test as written needs ~900 newcomer items.
- THE NEAREST-INCUMBENT CELL NO LONGER EXCLUDES 0; THE STREAK ENDS AT SIX. Delta 0.0078 [0.0023, 0.0134] at p = 0.10, against 0.0127 at p = 0.000 (#12) and 0.0077 at p = 0.04 (#11). The pool-size sweep added to weather_nn_validate.py shows the construction's magnitude is FLAT across the pool sizes this series has used (0.0116, 0.0137, 0.0122, 0.0134, 0.0114 at pools of 547-2089 under one fixed separation), and that at q = 308 a true delta of ~0.012 reaches p <= 0.02. So this is a smaller separation, not only a precision loss. The pooled window still excludes 0 (0.0081 [0.0055, 0.0106]) but shares 64.6% of its items with #12's.
- PLACEMENT IS FLAT FOR A SEVENTH ISSUE: bge lisp 1.223 (1.228), sci 0.656 (0.657), hn 0.608 (0.609); mpnet lisp 1.259 (1.273); gte lisp 1.065 (1.063). ISSUE #3'S UPGRADE TRIGGER DOES NOT FIRE. The gte window arm reads 1.058 against its < 1.0 bar. The bge window series reads 1.192, 1.192, 1.207, 1.215, 1.195 across #9-#13, so this issue banks the FIRST decline after two rises and the arm cannot complete before issue #15. All four windows since #10 hit the m = 1500 cap.
- THE SUB-FORTH DIP RATE APPEARS TO HAVE RISEN AND HAS NOT. Published basis 23.5% (16/68) against 13.0% (9/69), Fisher p = 0.1265. Placeholder-free, on a matched basis, 12.3% (8/65) against 24.2% (16/66) -- half of this issue's sub-forth windows are collapsed-comment boilerplate and the clean cell is flat. The 23.5% is published for continuity and NOT READ. Published series across thirteen issues: 10.3, 15.6, 30.8, 32.0, 47.6, 42.1, 10.5, 11.8, 4.8, 26.7, 16.7, 13.0, 23.5.
- THE SHARED-PREFIX ASSERTION HOLDS: 0 of 550 shared windows moved. All 3 backfilled items landed on 08-25, after the last window issue #12 published. Issue #12's violation came from backfill into an already-published day, and this issue is consistent with that diagnosis.
- REGISTER HELD ITS SERIES HIGH BY A MOVE OF EXACTLY ZERO. 08-25 reads 0.6597, identical to 08-24 to four decimals, where the median absolute day-to-day move is 0.0047. Twenty-day span 0.6367-0.6597 (range 0.0230), 0.0443 below the 0.704 human band floor. Whole-corpus 0.6489 -> 0.6500.
- THE FEED-LAG SHAPE THAT BROKE AT ISSUE #12 IS RESTORED. 3 backfilled items, all on 08-25, 0 authors revealed, median age 0.02 h and p90 0.04 h -- all three the pull-boundary race that held for nine issues. Issue #12's ~8-hour items came from a one-time 24.7-minute blind window, now guarded and quiet. Derived record for #3-#13: 0, 1, 3, 0, 1, 0, 2, 7, 3, 6, 3; per thousand window items 0.00, 1.03, 1.35, 0.00, 1.92, 0.00, 2.39, 2.94, 1.38, 2.17, 1.11.
- BACKFILL COUNTS ARE NOT LIKE-FOR-LIKE ACROSS THE FETCH-STRATEGY CHANGE. Under the retired full-pull-per-issue regime backfill measured the feed alone; under catch-up fetching it also measures SWEEP COVERAGE. Issues #3-#10 are the former, #11 straddles, #12 and #13 are the latter. Compare margins, traffic AND coverage before comparing counts.
- THE MUTATION AUDIT IS A SAMPLE, NOT A CENSUS, AND IS LABELLED ONE FROM THIS ISSUE ON. Zero edited items across 10,243 items re-verified since issue #12's pull -- 40.8% of the OBSERVATION STORE'S 25,134 items, in 644 of 2,396 threads (26.9%). That denominator is the store's, not this issue's 24,812-item analysis corpus (it counts every item-key ever observed, including the 234 post-cutoff items and everything below the 20-character rule); against the analysis corpus it is 41.3%. Issue #12's watch item #7 asked for a choice between raising the sweep budget and calling the audit a sample; THE RULING IS THE SECOND. What is published is the bound: 0 of 10,243 gives a one-sided 95% upper bound of 0.029% on the per-issue edit rate OVER THE VERIFIED SLICE. It does NOT extrapolate to the corpus -- the feed names active threads and the sweep scores by staleness, so the slice is not random.
- TWO COVERAGE NUMBERS ARE PUBLISHED AND THEY ARE DIFFERENT CONSTRUCTIONS. cutoff_margin.coverage is 40.3% of threads verified within 24 hours; feed_lag.content_mutations.audit_coverage is 26.9% verified since the PREVIOUS ISSUE'S PULL. The audit rests on the second. They coincided at issue #12 (both 30.5%) because exactly one fetch run sat in that window.
- NOTHING PUBLISHED IN ISSUE #12 MOVED. Derived by diffing the two records: no retained day gained items (all 3 backfilled landed on 08-25), no published venue share moved (the 148 outstanding 08-24 answers were retried and none resolved), 0 of 550 shared rolling windows moved, and every register value 08-06..08-24 is bit-identical.
- TWO ARITHMETIC SLIPS IN ISSUE #12'S CAVEATS BLOCK, noted here rather than by editing a published issue. Its backfill-per-1000 list read '0.00, 0.60, 1.66, 0.00, 1.28, ...' where its report body and results.json both read '0.00, 1.03, 1.35, 0.00, 1.92, ...'; the latter is correct. Its incumbent-only 5-day range read '2.9 points' where the body read 3.0; 94.3 - 91.3 = 3.0, and 3.0 is the number issue #11's rule was set against. Neither changes a reading in issue #12.
- Both allocation parses are published; the STRICT series remains the currency, as adopted at issue #8. Coverage is 24,645/24,811 (99.3%); all 166 uncovered items return a known WORLD phrasing and none resolved on retry, so the failure is one-sided for an eighth consecutive issue and the strict series is an upper bound on venue share.
- THE NEWCOMER/INCUMBENT ALLOCATION DIFFERENCE IS NOW TWO POSITIVE AND TWO NEGATIVE: +0.0365 (08-22, n=1450), +0.0331 (08-23, n=388), -0.0182 (08-24, n=894), -0.0342 (08-25, n=307, p = 0.2705). None individually significant. Issue #12's withdrawal of issue #11's reading stands and this issue adds nothing to it.
- Allocation currency. Venue share is the Qwen binary classifier. The LEVEL carries the allocation study's 0.31-0.71 specification range; kappa(Qwen, Gemma) is 0.4278 on this pool. The TREND is the cleaner object.
- The lemmy reference is FROZEN: a fixed 2023 corpus read from results/lemmy_baseline, not re-measured per issue. Platform share 0.4665 [0.4515, 0.4853]; corrected point 0.4660. The comparator's frame biases toward the square reading LOW (55.7% meta-tier).
- THE DAY-WINDOW CELLS CARRY AN EXPANDING-SPAN CONFOUND: 'core' means active on >= 3 calendar days over however long the corpus happens to be, so each issue gives every cohort another day to qualify AND adds a cohort to the average. core_n went 343 -> 396 and dominance 81.8 -> 82.7 this issue; both are reported, not read.
- Accumulation statistics. The rolling halves (0.1313 -> 0.1314) and the pooled dip share (21.0%) average over history that grows each issue; the issue-local equivalents are the primary readings.
- Overlapping-window moves are not independent confirmations. Consecutive trailing 5-day allocation means share 4 of 5 days; consecutive fixed-span structure cells share 4 of 5 (and 6 of 7) span days; the pooled newcomer window shares 64.6% of its items with issue #12's. No significance is attached to any of these runs.
- Retired series. core_n (issue #5); the fixed-horizon permeability running mean (#6); the fixed-span permeability row (#7); issue #5's three-day allocation rule (#8, confirmed at #10); the n >= 5 per-cohort conversion trend (#10); and issue #10's gap-based incumbent-allocation branch (#11, withdrawn as ill-posed).
- Single-normalizer / bge-only cells. The rolling series and all newcomer cells are Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone. bge is the named embedder for issue #3's window-decline trigger, as declared at issue #9.
- Activity-clock signatures compare at matched item volume over the anchors' FULL histories and are reported, not read: the move tracks arrivals, the same recruitment confound demonstrated for the fixed-span cells. These are NOT 'young phase' comparisons.
- A per-author daily cap of 20 COMMENTS is a platform rule, verified again this issue. Day volume is therefore active authors times an intensity bounded by ~21; 08-25 ran 424 active authors at 6.38 items each.
- The claimify batch is 8 for a fifth consecutive issue. 08-21 through 08-25 are all downstream of batch-8 claims; comparisons among them do not span the instrument change, comparisons against an EARLIER day still do.
- Identity != operator (permanent): author identities are forum identities, not distinct operators; concentration and retention readings are about identities. The influx profile's model-label column uses the platform's own label and is not an author clustering.
