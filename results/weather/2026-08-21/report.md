# 1f916 weather · 2026-08-21 (issue #9)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: full pull at 2026-08-22 01:46 UTC (last in-scope item 08-21 23:59:00), hard cutoff
**2026-08-22 00:00 UTC**. In scope: **14,785 items** (≥ 20 chars), 605 authors, Aug 5 → Aug 21
(complete, 1.8 hours of margin — back in line with issues #3–#7 after issue #8's 23.7). Issue
window: **836 items, all of 08-21**. Two things dominate. First, the statistic issue #8 named as
the **sole decider** for this issue **crossed its bound** on the first issue it could: the trailing
5-day allocation mean reads **0.4465** against 0.4515, the first time in the series, on a day whose
venue share (**0.4265**) is the lowest recorded. Issue #8's condition was "goes below **and
stays**", so this is half of it and issue #10 settles the rest. Second, the square took its
largest author influx since the founding week — **71 new authors** after two days at five — which
reversed issue #8's inflow "regime" reading, revived a newcomer instrument that had been dark for
three issues, and knocked the controlled concentration cells down at both widths. Those two facts
arrive on the same day and the obvious link between them is **tested and rejected**: newcomers did
not allocate less venue-ward than incumbents — the difference runs the wrong way for a
compositional explanation. Separately, this issue **corrects the window basis** —
under the old rule issue #9's window would have been 27 items, and the old rule turns out never to
have been a stable definition at all.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow spiking to 71 after a long decline to five; register falling back from its series high to mid-band; daily venue share dropping to a series low below the lemmy.world platform line, drawn under both parses.](figure.png)

## Readings

**Allocation — the pre-registered decider crossed the bound, which is half of its condition.** The series ran
0.4484 (08-17) → 0.4508 → 0.4367 → 0.4699 (08-20) → **0.4265** (08-21). That is the lowest daily
value the series has recorded, below the previous low of 0.4367, and it puts the day at **0.914×**
the [lemmy.world](../../lemmy_baseline/report.md) platform point estimate (**0.909×** with both
sides corrected), i.e. clearly below a human platform's founding month.

Issue #8 retired issue #5's three-day rule and named one replacement, in one sentence, as the only
thing that would decide the question: *the trailing 5-day mean against the 0.4515 bound, and only
that.* It reads 0.4804 (08-16) → 0.4789 → 0.4713 → 0.4589 → 0.4556 (08-20) → **0.4465** (08-21).
**That is the first time the smoothed statistic has ever gone below the bound.**

Being exact about what that buys, because the previous two issues have both over-read this cell in
opposite directions. Issue #8's condition was that the trailing mean *"goes below 0.4515 **and
stays**"*. It has gone below. It has not yet stayed — that takes issue #10 — so **the retirement
of issue #5's three-day rule remains provisional** and the question of whether issue #7 or issue #8
was reading the level correctly is not yet settled.

Two things temper it further, and both cut against the framing this report would prefer. **The
crossing is shallow relative to the statistic's own noise**: its depth is 0.0050, while the
counting standard error on a five-day mean of ~800-item days is roughly 0.008, and this report's
own account puts daily moves at ±0.02–0.05. And **on this particular transition the smoothing
bought nothing**: 08-16's 0.4720 rotated out of the window, so the five-day mean crossed if and
only if the new day itself came in below 0.4515 — a condition the *daily* series had already met
three times, on 08-17, 08-18 and 08-19. "A statistic designed to be hard to fire" is a fair
description of the rule in general and **not** of what happened here; on 08-21 it was exactly as
easy to fire as the daily rule it replaced. What the crossing does establish is that the level is
now low enough for the smoothed statistic to reach the bound at all, which it never was during the
excursion issue #7 called sustained.

**The daily direction remains not decidable** and the clustering test has weakened. Three of the
last five daily moves are negative, which fair-coin signs produce half the time (p = 0.5). The
exact permutation test on clustering now reads **p = 0.0929** over 16 days with 4 below the bound
(it was 0.0286 over 15 days with 3), because 08-20 sits between 08-19 and 08-21 and breaks the run
— which is the same instability that got the run rule retired, showing up as the run rule's own
statistic getting worse while the level got lower.

**The influx does not explain the low, and this was worth checking rather than assuming.** 08-21
carried 198 newcomer items against 632 incumbent, so the obvious alternative reading is
compositional: a flood of new arrivals who talk about the world rather than the venue. That is
testable from labels already in hand, and `analysis/weather_alloc_by_cohort.py` tests it against a
permutation null holding the day's share and both group sizes fixed. On the **strict parse**, which
is the series currency, **newcomers read 0.4293 and incumbents 0.4256** — a difference of +0.0037
in the *opposite* direction to the compositional story, p = 0.9312. Had newcomers allocated exactly
like incumbents, the day would have read 0.4256 against its actual 0.4265, so the entire
compositional contribution to the record low is **0.0009**. The corrected parse gives the same
answer on the same side (newcomers 0.4271, incumbents 0.4223, +0.0048, p = 0.9375, counterfactual
0.4223 against an actual 0.4234), and both are published.

Two limits. The test has power only for large differences, so the defensible statement is **not**
"newcomers allocated identically" but "the difference does not run the way the compositional story
needs" — it runs the other way under both parses, which is what kills that story arithmetically
rather than statistically. And it is one day's decomposition, not a causal claim about why anyone
allocates as they do.

**One asterisk on the word "record", and it is the batch change, not the classifier.** A CUDA OOM
forced this issue's claimify step down from batch 16 to batch 8 (method notes below). The
allocation classifier reads the *claims*, not the raw posts, so **08-21 is the only day in the
series whose labels sit downstream of claims generated under the new batch size** — every other day
came from batch-16 claims. This series has itself documented that batch composition perturbs
borderline decodes (issue #6 saw roughly 1 label in 66 flip from padding alone), and on an 836-item
day that mechanism is worth about ±13 items. The record-low *ranking* needs only 8.5 items to
overturn (0.4265 against the previous low 0.4367 is 0.0102 × 836), so **"lowest daily value the
series has recorded" is inside the instrument-change noise and should be read as "at the bottom of
the series", not as a clean record.** The two conclusions that carry weight need more: the
trailing-mean crossing needs about 21 items of the day to move, and the below-platform reading
(0.4265 against 0.4665) needs about 33. Those are outside the mechanism's scale; the record label
is not.

**Level caveat unchanged**, and the comparator's bias now runs *against* the reading rather than
for it — the reverse of issue #8. The absolute number carries the allocation study's 0.31–0.71
specification range; lemmy.world's 55.7% meta-tier frame makes the human benchmark more
self-referential than a neutral platform would be, which biases toward the square reading low, so
a below-platform day is the reading that bias favours. Eleven of sixteen classified days sit above
the platform figure and five below, under both parses.

**Label coverage — stable and still one-sided.** The uncovered count went 87 → **93**: the same 87
items plus 6 new on 08-21. All 93 return the verbatim string `SUBJECT MATTER`; zero of the 87
carried forward resolved; `published_days_moved` is empty for the third consecutive issue. Coverage
is 14,692/14,785 (**99.4%**). The corrected parse moves 08-21 from 0.4265 to **0.4234**, and the
corrected series is published beside the strict one as adopted at issue #8, with the strict series
remaining the cross-issue currency.

**Structure — the inflow collapse ended, hard.** New authors per day: 5 → 5 → **71**. Issue #8's
watch item #3 set the two branches: *a third consecutive day at or below 6 makes the inflow floor
a level; a return to 8+ says the whole 5–11 band since 08-14 is scatter.* The second branch fired
and then some — 71 is the **second largest single-day inflow of the series**, behind only the
founding day's 224 and ahead of 08-07's 64. Newcomer item-share went 0.010 → **0.238**. Active authors
118 → **177**. And daily item volume rose 702 → **836**, its first rise after three consecutive
falls and the highest daily volume since 08-15. (Not the series' first rise: volume also rose on
08-09, 08-10, 08-13 and 08-17.)

So the "regime" reading issue #8 published lasted exactly one issue, and the honest summary is
that neither issue #8's floor nor this issue's spike is a level: the inflow series has now produced
5, 5 and 71 on three consecutive days, and one day is not a trend in either direction. What is
established is that the collapse was **not** a floor.

The published day-window cells barely moved — core_n 226 → 229, dominance 90.6 → 90.0, stability
1.19 → 1.21, permeability 47.2 → **48.2** — and still carry the expanding-span confound, so they
are reported and not read.

Under the fixed-observation-span control:

| fixed span | #4 | #5 | #6 | #7 | #8 | **#9** |
|---|---|---|---|---|---|---|
| core dominance %, 7-day | 85.8 | 91.3 | 91.8 | 91.7 | 93.8 | **92.2** |
| core dominance %, 5-day | 86.4 | 87.6 | 88.4 | 91.0 | 93.2 | **89.1** |
| stability ratio, 7-day | 1.34 | 1.24 | 1.25 | 1.19 | 1.17 | **1.23** |
| stability ratio, 5-day | 1.35 | 1.32 | 1.32 | 1.25 | 1.22 | **1.34** |

**Both widths fell, so issue #8's "concentration is rising" reading does not survive its first
test.** Issue #8's watch item #4 required *a second consecutive rise at both widths*; instead the
5-day cell dropped 4.1 points and the 7-day 1.6, and stability rose at both widths after three
issues of falling. The mechanism is not mysterious — 71 new authors is exactly what dilutes a
concentration measure — but that is the point worth carrying: this cell moves with inflow, and the
series has now read 91.7/91.0 (#7), 93.8/93.2 (#8), 92.2/89.1 (#9) at the two widths in three
issues. **Neither "rising" nor "plateaued" is available**, and the whipsaw is a property of the
instrument plus one influx day, not three findings.

The uncomfortable corollary, which issue #8 did not consider and this issue should: if a single
influx day moves this cell four points, then the long "rise" of issues #5–#8 coincided with the
inflow *collapse* and may be the same coupling running the other way. That does not make the
earlier readings wrong, but it does mean the cell has never been shown to measure concentration
independently of recruitment, and no issue has controlled for it.

The retired fixed-span permeability row reads 55.6 → 52.8 (7-day) and 63.7 → 56.3 (5-day). It is
not read.

**Per-cohort conversion — the n ≥ 10 cell is frozen for a fourth issue, and the n ≥ 5 primary
oscillated.** At the old floor, N=3 is again bit-identical (r = +0.0908, p = 0.0444, 497 authors,
10 cohorts) — a fourth consecutive re-report of the same number, which is why issue #8 moved the
primary. At the n ≥ 5 primary:

| horizon | cohorts | authors | r | p | (issue #8) |
|---|---|---|---|---|---|
| **N=3 (primary)** | 15 | 529 | **+0.0917** | **0.0352** | +0.1036, 0.0188 |
| N=4 | 14 | 524 | +0.0931 | 0.0308 | +0.0840, 0.0600 |
| N=5 | 13 | 516 | +0.1121 | 0.0103 | +0.0953, 0.0321 |

Issue #8's watch item #5 asked whether the next entering cohort would push the primary back above
0.05 — *"if it does, the cell is tracking small-cohort noise and should retire rather than
oscillate."* **It did not**, so by the letter the direction survives. By the spirit it is closer:
the entire move from +0.1036 to +0.0917 is the entry of **one 5-author cohort** (08-19, converting
at 20.0%), the shared 14 cohorts reproduce issue #8's number exactly, and across three issues the
primary has read p = 0.0477, 0.0188, 0.0352 — wandering inside a narrow band under whichever
6-to-11-author cohort last closed its window. **Direction positive at all three horizons and both
floors; effect still not established; and the cell is now demonstrably one small cohort wide.**

**Newcomer — the per-issue cell is back after three dark issues, and it took both of this issue's
events.** The window carries **199 newcomer items against 637 incumbent**, clearing the floors
(m ≥ 100 for the parity and union cells; m ≥ 50 newcomer and ≥ 150 incumbent for the NN cell) for
the first time since issue #5. That needed the influx *and* the window-basis change: under the old
pull-based basis the entire window would have been 27 items and the cell dark whatever the inflow
did. Attributing the revival to the influx alone would understate the role of this issue's most
scrutinised decision.

| per-issue window cell (199 newcomer / 637 incumbent) | reading |
|---|---|
| within-pool parity | **0.988** [0.937, 1.030] |
| union over incumbent | **1.015** [0.980, 1.047] |
| nearest-incumbent distance, matched pools | Δ **0.0166** [0.0093, 0.0235], p = **0.008** |

The pooled cell agrees: 218 newcomer / 1,842 incumbent over 2.88 days, Δ **0.0178** [0.0122,
0.0238], p ≈ 0.000. Both say the same thing the pooled series has said since issue #7 —
**displaced but not diversifying**: newcomer claims spread internally about as widely as incumbent
claims and add no effective distinct content to the pool (both bands span 1), but sit measurably
farther from the incumbent cloud than incumbents sit from each other.

Two disciplines. The per-issue cell is **not** a continuation of the issues #1–#5 per-issue series,
because the window basis changed this issue and those cells were built on pull-based windows. And
the pooled cell still shares **59.4%** of its items with issue #8's (1,224 of 2,060), so
consecutive pooled points remain strongly dependent and are not a two-point trend.

**Placement — full-pool flat; the window cells are not comparable to anything yet.** Full-pool bge:
lisp **1.229** (1.221), sci **0.658** (0.660), hn **0.612** (0.613); mpnet lisp **1.253** (1.262)
and gte lisp **1.066** (1.064). Every move sits far inside its own band (bge full lisp
[1.199, 1.259]). The narrowing that ran through issues #2–#6 remains stopped rather than reversed,
now for a third issue.

Window-only cells (m = 668) read bge lisp **1.192**, mpnet **1.215**, gte **1.051** — and they are
**not read against issue #8's**, because this issue's window is built on a different basis. The
comparison restarts at issue #10.

**Issue #8's watch item #6 required this issue to name the embedder for issue #3's window-decline
trigger, and the naming is: bge.** That matches every other single-embedder cell in the report,
which are all bge-embedded and Qwen-normalized; mpnet and gte stay as the robustness check they
have always been. Two things have to be said with it. The option being declined is the one that
*fired*: mpnet's window cell had declined monotonically across all four prior one-day windows
(1.220 → 1.194 → 1.159 → 1.120), which is why issue #8 listed mpnet-primary explicitly rather than
quietly omitting it. And that mpnet run has now **broken anyway** — its window cell reads 1.215
this issue — though on the new basis, so the break is not evidence either. Per issue #8's
condition, the named trigger's first actionable application is to windows after 08-20, which means
issue #10 at the earliest.

**Idea series — the dip rate hit a series low and the prefix held.** Over the **21 windows this
issue added**, the sub-forth dip rate is **4.8%** (1/21), against 11.8% (2/17) at issue #8 and
10.5% at issue #7. That is the lowest the cell has recorded, and it is a third consecutive issue
out of the 40s — but 1/21 against 2/17 is Fisher two-sided p = 0.5768, indistinguishable, and the
windows overlap threefold so even that is anti-conservative. **Three issues in the 4–12% range is
the reading; the ordering within them is not.** The new-window mean is 0.1316 (0.1330). The pooled
share fell again, 22.5 → 21.5%, which is composition.

**The shared-prefix assertion passed for a second consecutive issue** — 0 of the 346 shared windows
moved, as required by 0 edited items over 14,756 compared.

Rolling halves read 0.1347 → **0.1300** (issue #8: 0.1350 → 0.1297), so the cross-issue second-half
series is #5 0.1298 → #6 0.1295 → #7 0.1295 → #8 0.1297 → **#9 0.1300**, a second consecutive tick
up on an accumulation statistic that is reported for continuity and not read. At 0.1300 the series
sits 2.4% above forth's **0.1269**, inside the forth-to-sci corridor where it has been every issue.

**Register — the series high was a single day, exactly as the alternative branch specified.** Daily
raw zstd: 0.6509 (08-19) → 0.6571 (08-20) → **0.6470** (08-21). Issue #8's watch item #7 read: *two
more days at or above 0.6510 would make this the first sustained register movement of the series; a
return to the 0.644–0.650 middle makes 08-20 a single high day.* **The second branch fired.** 0.6470
is squarely mid-band, and the sixteen-day series (08-05 falls below the 50-item floor) spans
0.6367–0.6571 and still sits **0.047 below the 0.704 human band floor** it has never approached. No
previously published register figure is revised, because no item was edited.

**Feed lag — two backfilled items, and this issue's count IS comparable to the earlier ones.** The
block finds **2** backfilled items on 08-21, aged 0.1 h at the missed pull, revealing **1 new
author**. That matters mainly as a reminder that backfill can move author-level cells, and 71
arrivals is the wrong week to assume it cannot. The pull margin was **1.8 h**, in line with issues
#3–#7's ~3 h, so unlike issue #8's 23.7-hour zero this count sits on the same instrument
sensitivity as the earlier ones. Derived across issues #3–#9 the backfill record is 0, 1, 3, 0, 1,
0, **2** — seven items over seven boundaries, every one minutes old at the missed pull, which
remains a pull-boundary race rather than a lagging feed. Trailing-day numbers stay provisional.

## The window basis, and why it changed

Issue #9's window would have been **27 items spanning 18 minutes** under the rule issues #1–#8
used, because that rule started the window at the previous *pull's* last item and issue #8 ran a
day late, pulling at 08-21 23:42. Roughly 800 items of 08-21 would have entered every full-pool
cell and no issue's window cells, ever.

The fix is to start the window at the previous published issue's **cutoff**, which is the boundary
the analysis actually used. That is a correction to intent rather than a new convention — the
author's standing understanding was that the window had always been cutoff-to-cutoff, and for
issues #3 and #4 it effectively was.

**The alternative was to publish the 27-item window this issue and switch at issue #10**, which
would have separated the decision from the issue that benefits from it. That was declined because
it would have thrown away a whole issue's window cells to buy a cleaner-looking sequence, and
because the defect is in the old rule rather than in this issue's data. The change is applied and
invented in the same issue, which is worth stating plainly rather than leaving for a reader to
notice, and it is why no window-only series is read across the boundary here.

The more useful finding is what the fix exposed about the old rule, which was never a stable
definition:

| issue | window items | that day's items | coverage | window start |
|---|---|---|---|---|
| #3 | 1,044 | 1,056 | 98.9% | 08-13 00:08 |
| #4 | 968 | 994 | 97.4% | 08-14 00:05 |
| #6 | 531 | 759 | 70.0% | 08-18 04:31 |
| #7 | 521 | 746 | 69.8% | 08-19 02:50 |
| #8 | 511 | 702 | 72.8% | 08-20 02:45 |
| **#9** | **836** | **836** | **100.0%** | **08-21 00:00** |

(Issues #2 and #5 followed multi-day gaps and were never one-day windows at all.) So "one-day
window" has meant anywhere from 70% to 99% of a day, drifting with whatever time the previous pull
happened to run, and the reports' grouping of #4/#6/#7/#8 as like-kind was already approximate.
Issues #3 and #4 were effectively cutoff-based; #6–#8 were not. This issue's window is the first
that is exactly one calendar day.

The consequence for this issue is that **no window-only series is read across the #8/#9 boundary**.
Window cells are reported and the comparison restarts at issue #10, which will be the first pair
built the same way. The boundary logic now lives in one stdlib-only module
(`analysis/weather_issue_boundary.py`) that both halves of the pipeline import, because the CPU
half runs under `.venv` and the GPU half under conda.

## Issue #8's watch items, answered by name

1. **Parity or above, decided by the trailing 5-day mean.** — **it went below the bound**, 0.4556 →
   **0.4465** against 0.4515, on a day that set a record-low venue share (0.4265, 0.914× platform).
   That is half of issue #8's condition; "and stays" is issue #10's. The three-day rule's
   retirement stays provisional.
2. **Does the strict parse stay the currency?** — **yes, unchanged.** The uncovered count grew 87 →
   93, all still `SUBJECT MATTER`, all still one-sided, no published day moved. The growth is 6
   items on a 836-item day; nothing warrants a currency break yet.
3. **A third day at or below 6 new authors?** — **no; the scatter branch fired and overshot.**
   71 new authors (the series' second largest, behind only the founding day's 224), newcomer share
   0.238, active authors 177, and the first rise in daily item volume after three consecutive falls. Issue #8's inflow "regime" did not survive one issue.
4. **A second consecutive rise in controlled dominance at both widths?** — **no; both fell**
   (93.8 → 92.2 and 93.2 → 89.1), with stability rising at both widths. "Rising" is withdrawn;
   "plateaued" is not available either.
5. **The n ≥ 5 cohort trend's next entering cohort.** — **it did not push p back above 0.05**
   (0.0188 → 0.0352), so by the stated letter the direction survives — but the whole move is one
   5-author cohort entering at 20.0%, and the primary has now read 0.0477, 0.0188, 0.0352 across
   three issues.
6. **Name the embedder for the window-decline trigger.** — **bge**, consistent with every other
   single-embedder cell. Declining mpnet-primary declines the option that had fired; mpnet's run
   has since broken (1.120 → 1.215) on the new basis, so neither fact is evidence. First actionable
   application is issue #10.
7. **Register: sustained movement or a single high day?** — **single high day.** 0.6571 → **0.6470**,
   back into the 0.644–0.650 middle, which is the branch issue #8 wrote for exactly this.
8. **Pooled newcomer overlap.** — **59.4%** (1,224 of 2,060 items shared with issue #8's window),
   reported alongside the cell and explicitly not read as a trend.

## Watch items for issue #10

1. **Does the trailing 5-day mean STAY below 0.4515?** This completes the only condition issue #8
   pre-registered and settles whether issue #7 or issue #8 was reading the level. Below for a
   second issue: the level has moved and issue #5's rule was retired for the right reason but on
   the wrong day. Back above: the smoothed statistic oscillates too, and the allocation cell needs
   a different object entirely rather than a third threshold.
2. **Is the influx a step or a spike?** 71 after 5 and 5 is one day. A second day above ~20 makes
   it a recruitment event with a mechanism worth finding; a return to single digits makes 08-21 an
   outlier and means the last three issues have read inflow as collapse, floor, and recovery in
   three consecutive issues, none of which was a level.
3. **The first like-for-like window pair.** Issue #10's window will be the second built on the
   cutoff basis. Until then no window series exists; from then, issue #3's trigger applies to bge
   as named, and the mpnet/gte cells are the robustness check.
4. **Controlled concentration needs a rule that an influx cannot flip.** The cell has read
   91.7/91.0 → 93.8/93.2 → 92.2/89.1 in three issues at the two widths, and the last move is one
   day of arrivals. Issue #10 should either read it only against issues with comparable inflow, or
   state a minimum move that counts as a change.
5. **The n ≥ 5 cohort trend is one small cohort wide.** Three issues, three values of p between
   0.018 and 0.048, each move attributable to a single 5-to-8-author cohort. If issue #10 moves it
   again by the same mechanism, the honest conclusion is that the cell cannot resolve the question
   at this inflow and should be retired rather than reported quarterly.
6. **Did the allocation floor hold without an influx?** 08-21 combined a record-low venue share
   with a record-since-founding inflow, and the cohort decomposition says the two are unrelated.
   A second low day *without* an influx would remove even that coincidence.
7. **The dip rate at 4.8% is a series low** and the third consecutive issue in single-to-low-double
   digits. A fourth confirms the 40s of issues #5–#6 were the excursion; a return to the 20s+ says
   this cell is noisier than three issues can show.
8. **Newcomer cells now exist at two scales.** If the influx does not repeat, the per-issue cell
   goes dark again and the pooled cell is all there is. Report which cells are live each issue
   rather than letting the series silently change instrument.

## Method notes & caveats

- **Cutoff** 2026-08-22 00:00 UTC, exclusive; the pull ran **1.8 h** after it and the last in-scope
  item is 08-21 23:59:00, so no in-scope day is partial. **291** items dated 08-22 were pulled and
  excluded. 08-21 cells are labelled provisional as standing discipline.
- **The window basis changed this issue and the old basis was never stable.** See the section
  above: from issue #9 the window starts at the previous published issue's CUTOFF; issues #1–#8
  started it at the previous pull's last item, which produced windows covering 70% to 99% of a day
  depending on pull time. Under the old rule this issue's window would have been 27 items.
  `analysis/weather_issue_boundary.py` owns the logic and emits the coverage history.
- **No window-only series is read across the #8/#9 boundary.** Window cells are reported; the
  comparison restarts at issue #10.
- **Both allocation parses are published; the STRICT series remains the currency**, as adopted at
  issue #8. Coverage is 14,692/14,785 (99.4%); all 93 uncovered items return `SUBJECT MATTER`, the
  failure is one-sided, and the strict series is an upper bound on venue share.
- **The trailing 5-day mean crossed the bound for the first time, which is half of a pre-registered
  condition.** Issue #8's wording was "goes below 0.4515 **and stays**". It has gone below; whether
  it stays is issue #10's question, and issue #5's three-day rule stays provisionally retired until
  then.
- **The record-low venue share is not a composition effect.** Newcomers 0.4271 (n = 199) vs
  incumbents 0.4223 (n = 637), difference +0.0048, permutation p = 0.9375
  (`analysis/weather_alloc_by_cohort.py`). Incumbents alone read 0.4223. One day, a decomposition,
  not a causal claim.
- **The clustering test weakened as the level fell**: p = 0.0286 (15 days, 3 below, run of 3) →
  **0.0929** (16 days, 4 below, run still 3, because 08-20 breaks it). The run rule's own statistic
  getting worse while the level got lower is the clearest available illustration of why it was
  retired as a level test.
- **Allocation currency.** Venue share is the Qwen binary classifier. The LEVEL carries the
  allocation study's 0.31–0.71 specification range; κ(Qwen, Gemma) is 0.4278 on this pool. The
  TREND is the cleaner object.
- **The lemmy comparator's frame biases toward the square reading LOW** (55.7% meta-tier), which is
  the direction of this issue's reading — the reverse of issue #8, where it cut against the
  finding. Hold both loosely for the same reason.
- **The lemmy reference is frozen**: a fixed 2023 corpus read from `results/lemmy_baseline`, not
  re-measured per issue. Platform share 0.4665 [0.4515, 0.4853]; corrected point 0.4660.
- **The per-issue newcomer cell is computable again after three dark issues**, and it required BOTH
  the influx and the window-basis change — under the old basis the window is 27 items and the cell
  is dark regardless of inflow. It is NOT a continuation of the issues #1–#5 per-issue series, which
  were built on pull-based windows. Floors: m ≥ 100 (Vendi parity/union), m ≥ 50 newcomer and ≥ 150
  incumbent (NN); 199 clears all three.
- **The pooled newcomer window shares 59.4% of its items with issue #8's** (1,224 of 2,060).
  Consecutive pooled points are strongly dependent and are not a trend. Its start is inherited from
  issue #7's published window start, which was pull-based, so the pooled series also straddles the
  basis change.
- **Accumulation statistics.** The rolling halves and the pooled dip share average over history
  that grows each issue; the issue-local equivalents are the primary readings. The shared-prefix
  assertion held for a second consecutive issue (0 windows moved, 0 items edited over 14,756
  compared).
- **The day-window structure cells carry an expanding-span confound** and are reported uncontrolled
  and not read; the fixed-span control is the reading. This issue the control fell at both widths
  while the uncontrolled cell barely moved, which is what a 71-author influx does to a
  concentration measure mechanically.
- **Overlapping-window moves are not independent confirmations.** Consecutive trailing 5-day
  allocation means share 4 of 5 days; consecutive fixed-span structure cells share 6 of 7 (and 4 of
  5) span days. No significance is attached to either series' run of moves.
- **The per-cohort trend test** is three correlated horizons of one hypothesis with no multiplicity
  correction. At n ≥ 10 it is bit-identical for a FOURTH consecutive issue. At the n ≥ 5 primary the
  entire move from issue #8 is one 5-author cohort entering; the shared 14 cohorts reproduce issue
  #8's number exactly.
- **Retired series.** core_n (issue #5); the fixed-horizon permeability running mean (#6); the
  fixed-span permeability row (#7) — it moved 63.7 → 56.3 at 5 days this issue; and issue #5's
  three-day allocation rule (#8, provisionally, pending item 1 above).
- **Single-normalizer / bge-only cells.** The rolling series and all newcomer cells are
  Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone. From this
  issue, **bge is also the named embedder** for issue #3's window-decline trigger.
- **Activity-clock signatures** compare at matched item volume over the anchors' FULL histories:
  agent dominance 83.8% (83.9), stability 1.46 (1.38), permeability 40.7% (41.4), against anchor
  dominance 15.1–43.8%, stability 4.05–6.07 and permeability 3.7–7.8%. These are not "young phase"
  comparisons.
- **Feed-lag history**, derived rather than quoted: issues #3–#9 read 0, 1, 3, 0, 1, 0, 2. Compare
  pull margins before comparing counts — this issue's 1.8 h is comparable to issues #3–#7's ~3 h;
  issue #8's 23.7 h is not.
- **A CUDA OOM interrupted this issue's first GPU pass, and it DOES touch a cross-issue
  comparison.** The claimify step peaked at 19.88 GB against ~20 GB usable (1.66 GB of it allocator
  fragmentation) on an 836-item delta; the batch is now 8 rather than 16 and
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is set before torch initialises CUDA. Claims
  are generated once per item and cached, so only the 836 items of 08-21 are affected — but the
  allocation classifier consumes claims, so **08-21 is the only day in the series whose labels
  descend from batch-8 claims**, and every comparison of 08-21 against an earlier day spans an
  instrument change of documented nonzero sensitivity (issue #6: ~1 label in 66 flipped from padding
  alone, ≈ ±13 items on this day). The record-low ranking (8.5 items) sits inside that scale; the
  trailing-mean crossing (~21 items) and the below-platform gap (~33 items) sit outside it. Issues
  #1–#8's claims were produced by the previous script.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators; concentration readings are about identities.
