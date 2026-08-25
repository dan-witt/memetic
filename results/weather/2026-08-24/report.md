# 1f916 weather · 2026-08-24 (issue #12)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-25 03:56 UTC (last in-scope item 08-24 23:59:11), hard
cutoff **2026-08-25 00:00 UTC**. In scope: **22,107 items** (≥ 20 chars), 1,153 authors, Aug 5 →
Aug 24 (complete, 3.93 hours of margin). Issue window: **2,770 items, all of 08-24**. One fact
organises the issue and it corrects the last one: **08-24 is the largest day the square has
recorded** — 2,770 items against 08-22's 2,380, 489 active authors against 393 — and it brought
**220 new authors**. The inflow series now reads 5, 5, 71, 258, 70, **220** over 08-19…08-24.
Issue #11 was explicit that the recruitment had "not stopped, only fallen", so that is not what is
withdrawn; what is withdrawn is its **event-level framing** — that 08-23 was the event's third day
and had separated recruitment from traffic. On this issue's evidence 08-23 was a lull inside a
continuing event, and the separation it reported was one day of it. Three pre-registered items resolve,
two of them against the previous issue. **Issue #8's decider holds for a fourth consecutive
issue**: 08-24 read **0.4385** against a bar of 0.4539, the trailing 5-day mean is 0.4484 at a
depth of 0.50 counting SE, and four consecutive days now sit below the bound. **The bar itself
moved after publication** — backfill added three items to 08-23 and shifted it from 0.4542 to
0.4539 — which is exactly the risk issue #11's cold review named, firing one issue later. **Issue
#11's newcomer/incumbent allocation reading failed its first out-of-sample test**: the difference
it named as the object to track is **−0.0182** on 08-24, having been +0.0365 and +0.0331. And the
cohort hypothesis issue #11 raised is **refuted by its own pre-registered test** — 08-22's
258-author cohort entered at 35.3%, the highest of the five cohorts with n ≥ 50, against 08-21's
18.3%. Separately the CPU stage went from ~55 minutes to 11 seconds with a bit-identical register
series, and the feed-lag block broke a shape that had held for nine issues.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow showing a four-day event at 71, 258, 70 and 220 against a founding day of 224; register drifting up to a series high still far below the human floor; daily venue share falling to 0.4385, below the lemmy.world platform line, with 08-21's 0.4265 lower still.](figure.png)

## Readings

**Structure — the event has four days, not three, and 08-24 is the largest of them.**

| | 08-20 | 08-21 | 08-22 | 08-23 | **08-24** |
|---|---|---|---|---|---|
| new authors | 5 | 71 | 258 | 70 | **220** |
| active authors | 118 | 177 | 393 | 317 | **489** |
| items | 702 | 836 | 2,380 | 2,172 | **2,770** |
| newcomer item share | 0.010 | 0.238 | 0.613 | 0.179 | **0.325** |

**Issue #11's central structural reading is withdrawn.** It observed arrivals falling 258 → 70
while volume held at 91% of the record, and read that as the event separating recruitment from
traffic. 08-24 brings 220 arrivals and a new record on both volume and active authors, so the
supported description is a **four-day recruitment event with a one-day lull**, not an event that
ended. What issue #11 got right is the mechanism it identified — retained arrivals carry the
traffic — and that is now visible at larger scale: 08-24's newcomer item share is 0.325, so two
thirds of the record day came from authors who were already present.

The platform's 20-comment daily cap makes the arithmetic explicit. 08-24 ran **5.66 items per
active author**, *below* 08-23's 6.85 and inside the 5.95–7.65 band the square held before the
event. The record day came from recruiting, not from anyone posting harder — which is the only
way a day can get much bigger under the cap.

**Allocation — the decider holds for a fourth issue, and its bar moved underneath it.** The daily
series ran 0.4699 (08-20) → 0.4265 → 0.4653 → 0.4419 (08-23) → **0.4385** (08-24). The trailing
5-day mean reads 0.4465 → 0.4498 → 0.4480 → **0.4484**, against the bound of 0.4515. Four
consecutive days now sit below it (08-21…08-24).

Issue #11 pre-registered the exact bar: 08-24 below **0.4542**. Then backfill added three items to
08-23 and moved its share from 0.4416 to 0.4419, so the correctly recomputed bar is **0.4539**.
08-24 read 0.4385 and clears both by about 0.015, so **the conclusion is unaffected and the
mechanism is worth naming anyway**: a pre-registered threshold's own inputs moved after
publication. Issue #11's cold review flagged this as a live risk — the "iff" assumes the retained
days do not move — and it fired one issue later. From here a pre-registered bar is published
together with the day-values it rests on, so the next issue recomputes rather than inherits it.

The depth is unchanged in noise terms: 0.4515 − 0.4484 = **0.0031**, against a counting standard
error of **0.0062** for the five-day mean, i.e. **0.50 SE** — the same as issue #11, against 0.23
at #10 and 0.62 at #9. Three of the last five daily moves are negative (p = 0.50). The clustering
permutation reads **p = 0.2856** over 19 days with 6 below the bound and the longest run still 3,
weaker again than issue #11's 0.1716.

**Against the human platform, 08-24 is the most statistically resolved below-platform day — not
the lowest.** The day reads 0.4385 against [lemmy.world](../../lemmy_baseline/report.md)'s
**0.4665** platform point: a gap of −0.0280 on a day whose own binomial counting standard error is
**0.0095**, i.e. **−2.96 SE**, against −2.33 SE at 08-23 and −0.12 SE at 08-22. **In venue-share
terms 08-21 is lower** (0.4265, a gap of −0.0400); it carries fewer standard errors only because it
is a smaller day — 830 labelled items against 2,746 — so this superlative partly rewards 08-24 for
its size and is stated in SE units for that reason. Eleven of
nineteen classified days sit above the platform figure and eight below, under both parses. The
comparator's own interval ([0.4515, 0.4853]) is wider still, and none of this includes classifier
error.

**The newcomer/incumbent difference flipped sign, and issue #11's reading of it is withdrawn.**
Issue #11 withdrew issue #10's gap-based branch as ill-posed — the gap is identically
newcomer-weight × difference — and named the **difference** as the object to track, reporting
newcomers ~3.4 points more venue-ward on the two days large enough to resolve it. 08-24 is the
third such day:

| | newcomer share | incumbent share | difference | p |
|---|---|---|---|---|
| 08-22 (n = 1,450) | 0.4793 | 0.4429 | **+0.0365** | 0.0922 |
| 08-23 (n = 388) | 0.4691 | 0.4360 | **+0.0331** | 0.2310 |
| **08-24 (n = 894)** | **0.4262** | **0.4444** | **−0.0182** | 0.3844 |

None of the three is individually significant, and the third runs the other way. **The supported
statement is that this difference is not a stable property of newcomers.** Issue #11's ~3.4-point
reading survived exactly one issue, which is what tracking a testable object is for — it produced a
claim that could fail, and it failed. The incumbent-only trailing 5-day mean is **0.4433**, and
08-24's incumbents read 0.4444, *above* the day's published 0.4385.

**Per-cohort conversion — the hypothesis issue #11 raised is refuted by its own test.** Issue #11
found 08-21's 71-author cohort entering at 18.3%, the lowest of the cohorts with n ≥ 50, and
pre-registered that *two low cohorts in a row would be the first evidence that event-recruited
authors convert differently*. 08-22's 258-author cohort has now entered:

| N=3, cohorts with n ≥ 50 | 08-06 | 08-07 | 08-09 | 08-21 | **08-22** |
|---|---|---|---|---|---|
| conversion | 25.4% | 23.4% | 30.4% | 18.3% | **35.3%** |

**35.3% is the highest of the five**, and +8.7 points above the author-weighted pool of prior n ≥ 10
cohorts (26.6%, n = 568) at **+2.49 counting SE**. So the branch that fired is the one that says
08-21's low cohort was the outlier, not the pattern, and the "event-recruited authors convert
worse" hypothesis is not supported. The published N=3 cell moved 30.9 → **31.3**; 08-21 also
entered N=4 at 29.6%, moving that cell 37.6 → **36.9**; per-cohort identity across the boundary
**HOLDS** at all three horizons.

**Concentration — the uncontrolled cell rose this issue, for the same reason it fell last issue.**

| fixed span | #9 | #10 | #11 | **#12** |
|---|---|---|---|---|
| uncontrolled dominance %, 5-day | 89.1 | 61.4 | 52.1 | **66.8** |
| incumbents only, 5-day | 94.3 | 93.2 | 93.3 | **94.1** |
| uncontrolled dominance %, 7-day | 92.2 | 70.7 | 61.3 | **71.0** |
| incumbents only, 7-day | 95.9 | 96.3 | 95.8 | **94.5** |

The uncontrolled cell fell 37 points over issues #10–#11 and has now recovered 14.7 of them, while
the incumbent-only row moved 0.8. Nothing about concentration changed in either direction: 08-22's
258 arrivals have simply been present long enough to qualify as core (active on ≥ 3 days) instead
of diluting the denominator. That is the same expanding-opportunity mechanism, running the other
way, and it is the clearest demonstration yet that this cell tracks the age of an influx rather
than concentration.

**Issue #11's pre-registered concentration rule does not fire, and correctly so.** It required a
move of more than 3.0 points in the incumbent-only 5-day cell **on a day with fewer than 100
arrivals**. The move was +0.8 and the day carried 220 arrivals, so neither arm is satisfied. Across
issues #5–#12 that cell reads 91.3, 91.4, 93.6, 93.6, 94.3, 93.2, 93.3, 94.1 — a range of 3.0
points, which is why the threshold was set there.

**Newcomer — the first move this cell can actually see.** The window carries **901 newcomer items
against 1,869 incumbent**, against issue #11's 389/1,780.

| per-issue window cell | issue #12 | issue #11 |
|---|---|---|
| within-pool parity | **1.067** [1.048, 1.082] | 1.011 [0.978, 1.044] |
| union over incumbent | **1.050** [1.026, 1.074] | 1.017 [0.997, 1.046] |
| nearest-incumbent distance | Δ **0.0127** [0.0086, 0.0177], p = **0.000** | Δ 0.0077 [0.0026, 0.0126], p = 0.04 |

Both Vendi cells exclude 1 again — but the important difference from the #10/#11 comparison is
that **each issue's point estimate now sits outside the other's band**. Issue #11 could say only
that no change was detectable; here the instrument can see one. Two limits: *m* rose 311 → 720, and
a cell that has moved once is not a trend. The nearest-incumbent finding is the stable one and
excludes 0 for a **sixth** consecutive issue, more strongly than at issue #11. The pooled cell
agrees in direction (parity 1.033 → 1.055, union 1.026 → 1.036, Δ 0.0104 [0.0069, 0.0145],
p ≈ 0.000) and shares **62.2%** of its items with issue #11's, so consecutive pooled points remain
dependent and are not a trend.

**Placement — full-pool flat for a sixth issue; the window series is rising.** Full-pool bge: lisp
**1.228** (1.223), sci **0.657** (0.656), hn **0.609** (0.613); mpnet lisp **1.273** (1.265) and
gte lisp **1.063** (1.062).

| window-only | #9 | #10 | #11 | **#12** |
|---|---|---|---|---|
| bge lisp | 1.192 | 1.192 | 1.207 | **1.215** |
| mpnet lisp | 1.215 | 1.203 | 1.216 | **1.259** |
| gte lisp | 1.051 | 1.058 | 1.050 | **1.066** |

All three windows since #10 hit the m = 1500 draw cap, so band widths are comparable across
#10/#11/#12. **Issue #3's upgrade trigger does not fire.** The gte arm reads 1.066 against its
< 1.0 bar. The decline arm needs three consecutive declines in the bge window series; that series
has now risen twice, so zero declines are banked and the arm **cannot complete before issue #15**.

**Idea series — the dip rate fell again, and the shared-prefix assertion broke.** Over the **69
windows this issue added** the sub-forth dip rate is **13.0%** (9/69), against 16.7% at issue #11
(Fisher p = 0.61, and anti-conservative on overlapping windows). The comparison uses **16.7%**
deliberately: `weather_dip_rate.py` computes each issue's rate from that issue's own published
series, which is what keeps the per-issue series self-consistent. The **18.5%** below is what issue
#11's *windows* read against today's corpus — a different quantity, and not a replacement for the
published one. Over eight issues the cell has
read 47.6, 42.1, 10.5, 11.8, 4.8, 26.7, 16.7, **13.0** — the same 5–48% range with no ordering that
survives.

**The shared-prefix assertion is violated for the second time in twelve issues, and the first with
a consequence.** 13 of the 481 shared rolling windows moved — indices **468–480**, the *last*
thirteen, all dated 08-23 16:23 onward, which is exactly where the three backfilled items inserted.
One of them (window 478, 08-23 21:35) moved 0.1274 → 0.1259 and **crossed the forth anchor**, so
**issue #11's published dip rate revises from 16.7% to 18.5%** (9/54 → 10/54). That sits well
inside the cell's own range and changes no reading. Issue #7's violation (3 windows, 0 crossings)
was the first. The assertion is doing its job: it detected an insertion the pipeline would
otherwise have absorbed silently.

Rolling halves read 0.1329 → **0.1313**, an accumulation statistic reported for continuity and not
read. At 0.1313 the series sits 3.5% above forth's **0.1269**, inside the forth-to-sci corridor
where it has been every issue.

**Register — a series high on the largest day, reached by a typical step.** Daily raw zstd: 0.6496
(08-22) → 0.6543 (08-23, revised from the 0.6539 issue #11 published) → **0.6597** (08-24). That
is the highest value the series has recorded,
above 08-20's 0.6571. The move is **+0.0054**, where the median absolute day-to-day move is
**0.0053**. The nineteen-day span is now 0.6367–0.6597, a range of 0.0230, and the newest day sits
**0.0443 below the 0.704 human band floor**. Issue #11 concluded this cell is insensitive to
anything the square has yet done, and set the bar for a real move at more than the whole observed
range; **a record day moving it by exactly the median step is consistent with that**, and the
conclusion stands. One correction to issue #11, which wrote that no previously published register
figure was revised: 08-23's is, by +0.0004, because backfill added three items to that day.

**Feed lag — the standing shape broke, and the cause is the fetcher rather than the feed.** The
block finds **6** backfilled items, 3 on 08-23 and 3 on 08-24, revealing **0** new authors. Nine
issues had reported that every backfilled item was minutes old at the missed pull — a pull-boundary
race. This issue's six split cleanly, and **the split is the reading**; the median of 3.97 h
describes neither group:

- **three are the usual race**: 0.01, 0.04 and 0.11 h, created 08-24 01:13–01:19, minutes before
  issue #11's pull at 01:21;
- **three are ~8 hours old**: 7.82, 7.93 and 8.14 h, all created **08-23 17:11–17:30**.

(The cell published 7.82 h before this issue's review: `weather_cpu.py` took the upper-middle value
rather than a true median, which is correct only for odd *n*, and this is the series' first
even-count backfill. Fixed; the cell now reads 3.97 h, which is why the split is reported instead.)

The store's full pull ran at **17:12:19** while the changes-feed cursor was seeded at **17:31:47**.
The hole is measured from the newest item the pull actually held — **17:07:12** — to the cursor,
i.e. **24.7 minutes**, and a forward-only feed walk can never report it. Two of the
three are a post and a comment in thread 1810, whose post was created at 17:11 — one minute before
the full pull read it. They were recovered ~34 hours later, when this issue's run re-read
their threads — but **which mechanism recovered them is not established**. Both threads gained
comments after issue #11's cursor (thread 1810 at 08-24 02:10, 07:07 and 20:53; thread 960 at
02:11), so the changes feed would have named them anyway, and the run log records only a combined
target count. A draft of this issue credited the staleness sweep and called it the first direct
evidence the sweep catches what the feed cannot; that is withdrawn as uncheckable from the data,
and `corpus_fetch.py` should record feed and sweep targets separately so the next such case is
decidable. The blind-window diagnosis itself stands: all three items were created inside it. This
is a one-time bring-up artefact, not a property of the feed, and `corpus_fetch.py` now warns
whenever the cursor sits ahead of the newest item held (verified: it fires on the historical state
at 24.7 minutes, and is quiet now).

**Backfill counts are not like-for-like across the fetch-strategy change**, and this issue is the
first where that matters. Under the retired full-pull-per-issue regime every thread was re-read
every issue, so backfill measured the feed alone; under catch-up fetching it also measures **sweep
coverage**. Derived record for issues #3–#12: 0, 1, 3, 0, 1, 0, 2, 7, 3, **6** — and per thousand
window items 0.00, 1.03, 1.35, 0.00, 1.92, 0.00, 2.39, 2.94, 1.38, **2.17**, the scale issue #11
adopted.

**Zero edited items across the 9,135 items that were actually re-verified — 40.0% of the corpus,
in 30.5% of threads.** The `feed_lag` block also reports `items_compared` = 19,641, which is every
item known at the previous issue's pull and *not* what was compared; an edit is only detectable in
a thread re-read since then, so 9,135 is the number the audit rests on. Issue #11
reported 100% coverage and pre-registered that a catch-up-only issue would be far lower, because
its own 100% came from a full pull that happened to sit inside its window. That is now the case,
and the negative is correspondingly weaker.

## Revisions to issue #11

Backfill inserted three items into 08-23, a day issue #11 had already published. The series has
always labelled trailing-day numbers provisional; this is the first issue in which that label did
any work. Restated here rather than by editing the published issue:

| cell | issue #11 published | now reads |
|---|---|---|
| 08-23 items | 2169 | **2172** |
| 08-23 venue share (strict) | 0.4416 | **0.4419** |
| 08-23 venue share (corrected parse) | 0.4394 | **0.4397** |
| 08-23 incumbent-only share | 0.4356 | **0.436** |
| 08-23 raw zstd register | 0.6539 | **0.6543** |
| issue #11 trailing 5-day mean | 0.448 | **0.4481** |
| issue #11's sub-forth dip rate, recomputed on today's corpus | 16.7% (9/54) | **18.5%** (10/54) |
| the bar issue #11 set for 08-24 | 0.4542 | **0.4539** |

This table is **derived by diffing the two published records**, not enumerated by hand — the hand-written version of it missed three cells, including the register value issue #11 had explicitly said was not revised.

None of these changes a reading in issue #11. The dip-rate revision is the largest and sits inside
a cell whose issue-to-issue range is 5–48%.

## The instrument changes

**The CPU stage went from ~55 minutes to 11 seconds, and the register series is bit-identical.**
Issue #11 flagged that `zstd_curve.compute_metrics` is quadratic in corpus size. The reason is
`cond_full`, which rebuilds a level-19 zstd dictionary over the *entire* accumulated history once
per 25-item bucket — and which **no weather issue has ever read**; the register cell uses
`self_bits` and `cond_win_bits` only, and `cond_full` belongs to the standalone
[`zstd_curve`](../../zstd_curve/report.md) pass. Two changes follow:

- **`columns`** lets a caller pay only for what it reads. Dropping `cond_full` and `cond_shuf`
  removes the quadratic term outright, leaving a fixed 512 KB window per bucket. **48 seconds.**
- **`reuse`** makes the remainder incremental. Both retained columns are prefix-stable — appending
  later items cannot change an earlier item's value — so rows carry over from the previous issue.
  **11 seconds**, reusing 18,832 of 22,107 rows.

**Verified neutral, not assumed.** Re-running issue #11 pinned to its published `pull_at`
reproduced all eighteen per-day register values, the whole-corpus figure (0.6473), the corpus block
and the churn signature bit-identically. Three things break prefix-stability and are detected
rather than assumed: an edited item (hash mismatch), an item inserted mid-stream by backfill (key
mismatch, and it shifts every later bucket boundary because buckets are indexed from 0), and a
change to the compression parameters (the cache stores them and is discarded whole if they move).
`cond_full` is, in fact, prefix-stable in the same sense — its dictionary is the history before
the bucket — so it is dropped for **cost, not correctness**; an earlier draft of this issue claimed
it depended on later items, which is true only of `cond_shuf`, and that claim is corrected.
`cond_shuf` samples items regardless of time, including ones after the item being scored, so
requesting it alongside `reuse` raises rather than silently returning wrong numbers. This issue exercised the insertion path: the cache rewound 502 rows when it met the
backfilled items rather than trusting the prefix.

Reuse requires key, content hash **and position**. A key-and-hash check alone would miss a
*deletion*, which leaves every surviving key and hash intact while shifting later items onto a
history that still contains the removed item — a stale register series that would stay plausible to
four decimals. `analysis/zstd_reuse_validate.py` runs all five mutation paths (deletion, insertion,
edit, append, unchanged) from scratch and from cache and requires bit-identical rows; all pass, as
does the assertion that `cond_full` with `reuse` raises. Re-running this issue under the hardened
check reused 22,107 of 22,107 rows in **3.3 s** and reproduced `weather_cpu_out.json`
byte-identically.

**`corpus_verify.py` was run against this issue before the review, and caught an assembly bug.**
The runbook step added at issue #11 — verify the *new* issue, not just the previous one — found
`results.json` carrying the wrong `cutoff` on its first use, which would have made the issue
irreproducible from its own published stamp. Fixed; **14/14 cells reproduce**.

## What the influx looks like on its fourth day

| | 08-22 | 08-23 | **08-24** |
|---|---|---|---|
| new authors | 258 | 70 | **220** |
| hours of the day they arrived in | 24 / 24 | 23 / 24 | **24 / 24** |
| share in the busiest hour | 8% | 10% | **10%** |
| items per author (median / max) | 3 / 21 | 4 / 21 | **3 / 21** |
| items per active author | 6.06 | 6.85 | **5.66** |
| threads touched | 447 | 440 | **595** |
| median chars, newcomers vs incumbents | 1,282 / 1,256 | 1,178 / 1,641 | **1,213 / 1,409** |
| distinct platform model labels among arrivals | 101 | 46 | **98** |

08-24's arrivals look like 08-22's: spread across the whole clock with no hour above 10%, a median
of three items each, across **595 threads** — the most the square has seen — under 98 distinct
platform-provided labels. Nothing about the profile suggests a scripted onboarding or a single
operator, and as at every prior issue that is a *descriptive* negative: it rules out cheap artefact
explanations and cannot distinguish an organic influx from a well-distributed synthetic one. The
model-label column uses the platform's own label; it is not an author clustering, and identity
remains forum identity rather than operator.

## Issue #11's watch items, answered by name

1. **Does 08-24 read below the pre-registered 0.4542?** — **yes, 0.4385**, and below the corrected
   0.4539 as well. The trailing mean is 0.4484, a fourth consecutive issue below the bound at
   0.50 counting SE. The bar itself moved because backfill changed 08-23; the conclusion did not.
2. **What would move the incumbent-only concentration cell.** — **the rule did not fire, and
   correctly.** It needed > 3.0 points on a day with < 100 arrivals; the move was +0.8 on a day
   with 220. The uncontrolled cell rose 14.7 points on the same data, which is arrivals ageing into
   core membership.
3. **Does the traffic survive the arrivals — read as active authors?** — **the question was
   overtaken.** Issue #11 asked whether 08-24 would hold above ~250 active authors with arrivals in
   the tens. It held **489** active authors, but with **220** arrivals, so the test as written was
   not run: the event resumed instead. A narrower version *is* decidable and is reported here —
   **269 of the 489 active authors were incumbents**, above the ~250 bar, and they posted 1,869
   items without any help from 08-24's arrivals. So the retained cohort cleared the retention
   threshold on its own. Items per active author fell to 5.66, so the record day is recruitment,
   not intensity.
4. **08-22's 258-author cohort enters the N=3 table.** — **it entered at 35.3%**, the highest of
   the five n ≥ 50 cohorts and +2.49 SE above the pooled prior. Two low cohorts in a row would have
   been evidence; the second is the highest, so the hypothesis is not supported.
5. **What magnitude of event would move register.** — **answered and the answer held.** The bar was
   a move larger than the whole observed range (0.0204). The largest day on record moved it
   +0.0054, one median step, to a series high of 0.6597. The cell remains insensitive.
6. **Report audit coverage now that a full pull is not in the window.** — **30.5% of threads and
   40.0% of items**, against 100% at issue #11, exactly as predicted. "0 edited items" is reported
   with that denominator.
7. **Verify the new issue, not just the old one.** — **done, and it caught a real bug** on its
   first use: `results.json` carried the wrong `cutoff`. Fixed before review; 14/14 cells reproduce.
8. **The CPU stage's cost.** — **bounded rather than accepted.** ~55 min → 11 s, with the register
   series verified bit-identical against issue #11.

## Watch items for issue #13

1. **The decider's bar, published with the values it rests on.** For issue #13 the trailing window
   is 08-21…08-25, whose first four days are 08-21 **0.4265**, 08-22 **0.4653**, 08-23 **0.4419**
   and 08-24 **0.4385**, summing to **1.7722**. All four are revisable by label retry as well as
   by backfill, which is why the bar is published with them. The mean stays below 0.4515 if and only if 08-25
   reads below **0.4853**. That is by far the easiest bar the run has faced (0.4517, 0.4736, 0.4591,
   0.4539 preceded it), because the four retained days are all low — 08-25 would have to come in
   *above the platform point* to end the run. Recompute the bar from the four day-values before
   using it rather than inheriting 0.4853.
2. **Does the event have a fifth day?** Arrivals read 71, 258, 70, 220. Two of the four days were
   ~250 and two were ~70, which does not yet distinguish a decaying event from an oscillating one.
   Report arrivals and active authors together; if arrivals fall below ~30 while active authors
   hold above 400, the retention question issue #11 asked finally becomes answerable.
3. **Does the newcomer Vendi move survive?** This issue is the first where the per-issue cells moved
   outside the previous issue's bands (parity 1.011 → 1.067). One move is not a trend, and *m* rose
   2.3×. If issue #13 returns a similar point estimate at similar *m*, the cell has moved; if it
   falls back toward 1.02 the move was the 08-24 cohort specifically.
4. **The newcomer/incumbent allocation difference, now that it has changed sign.** Three large-n
   days read +0.0365, +0.0331, −0.0182. Report the fourth without a prior: this cell has now
   produced a reading and its reversal in consecutive issues, so any new claim about it needs more
   than one day.
5. **08-23's cohort enters N=3 and 08-21's enters N=5.** 08-23 brought 70 authors, a mid-sized
   cohort arriving in the event's lull. Report it against 08-21's 18.3% and 08-22's 35.3% — if
   conversion tracks arrival-day size rather than the event, that is a different mechanism from the
   one issue #11 proposed.
6. **Backfill under catch-up-only fetching, for the second issue running.** This issue's 6 included
   3 from a one-time cursor gap now guarded. Issue #13's count is the first clean measurement of
   what catch-up fetching alone leaves behind, and should be read against sweep coverage rather
   than against issues #3–#10.
7. **Audit coverage as a standing number.** At 30.5% of threads, the mutation audit covers well
   under half the corpus. Either raise the sweep budget so coverage stays above some stated floor,
   or state plainly that the audit is a sample and stop reporting "0 edits" as though it were a
   census. Issue #13 should pick one.

## Method notes & caveats

- Cutoff 2026-08-25 00:00 UTC, exclusive; the pull ran 3.93 h after it and the last in-scope item is 08-24 23:59:11, so no in-scope day is partial. 641 items dated 08-25 were pulled and excluded. 08-24 cells are labelled provisional as standing discipline -- and this issue is the first in which that label did real work; see revisions_to_published_issues.
- 08-24 IS THE LARGEST DAY THE SQUARE HAS RECORDED on volume (2,770 items against 08-22's 2,380) and on active authors (489 against 393), with 220 new authors. The inflow series now reads 5, 5, 71, 258, 70, 220 over 08-19..08-24, so THE RECRUITMENT EVENT DID NOT END AT 08-23. Issue #11 read 08-23 as arrivals collapsing while volume held and treated it as the event's third day; on this issue's evidence 08-23 was a lull inside a continuing event, and that framing is withdrawn.
- THE PRE-REGISTERED DECIDER HOLDS FOR A FOURTH ISSUE. Issue #11 published the bar (08-24 below 0.4542); backfill then moved 08-23 and the correct bar is 0.4539. 08-24 read 0.4385 and clears both by ~0.015. The trailing 5-day mean is 0.4484, a depth of 0.0031 = 0.50 counting SE (0.0062), the same depth as issue #11 and against 0.23 at #10 and 0.62 at #9. Four consecutive days now sit below the bound (08-21..08-24).
- A PRE-REGISTERED THRESHOLD'S OWN INPUTS MOVED AFTER PUBLICATION, which issue #11's cold review named as a live risk and which fired one issue later. published_days_moved is non-empty for the first time in the series. The mechanism is backfill, not classifier drift: 08-23 gained 3 items and its share moved 0.4416 -> 0.4419. Report a pre-registered bar with the day-values it rests on, so a later issue can recompute it rather than inherit it.
- 08-24 IS THE MOST STATISTICALLY RESOLVED BELOW-PLATFORM DAY, NOT THE LOWEST. It reads 0.4385 against lemmy.world's 0.4665, a gap of -0.0280 on a day whose binomial counting standard error is 0.0095, i.e. -2.96 SE, against -2.33 SE at 08-23 and -0.12 SE at 08-22. In venue-share terms 08-21 is LOWER (0.4265, a gap of -0.0400); it carries fewer SEs only because it is a smaller day (830 labelled items against 2,746), so this superlative partly rewards 08-24 for its size. Eleven of nineteen classified days sit above the platform figure and eight below, under both parses. The comparator's own CI ([0.4515, 0.4853]) is wider still, and none of this includes classifier error.
- ISSUE #11'S NEWCOMER/INCUMBENT ALLOCATION CLAIM FAILED ITS FIRST OUT-OF-SAMPLE TEST. Issue #11 withdrew the gap-based branch as ill-posed and named the DIFFERENCE as the object to track, reporting ~3.4 points more venue-ward for newcomers on the two days large enough to resolve it. 08-24 is the third such day and the difference is NEGATIVE: newcomers 0.4262 (n=894) vs incumbents 0.4444 (n=1,852), -0.0182, permutation p = 0.3844. The three large-n days read +0.0365, +0.0331, -0.0182, none individually significant. The supported statement is that this difference is not a stable property of newcomers; issue #11's reading is withdrawn.
- THE FEED-LAG INSTRUMENT BROKE ITS STANDING SHAPE, and the cause is the fetcher, not the feed. Nine issues reported that every backfilled item was minutes old at the missed pull -- a pull-boundary race. This issue's 6 items split: 3 were minutes old (0.01, 0.04, 0.11 h, created just before issue #11's pull) and 3 were ~8 h old (7.82, 7.93, 8.14 h). The SPLIT is the reading; the median of 3.97 h describes neither group. weather_cpu.py had been taking the upper-middle value rather than a true median, correct only for odd n -- this is the series' first even-count backfill and the cell published 7.82 before the fix. All three old items were created 08-23 17:11-17:30. The store's full pull ran at 17:12:19 while the changes-feed cursor was seeded at 17:31:47, leaving a 24.7-MINUTE BLIND WINDOW that a forward-only feed walk can never report; two of the three are a post and a comment in thread 1810, whose post was created at 17:11, one minute before the full pull read it. They were recovered ~34 h later when this issue's run re-read their threads. WHICH MECHANISM recovered them is NOT established: both threads gained comments after issue #11's cursor (thread 1810 at 08-24 02:10, 07:07 and 20:53; thread 960 at 02:11), so the changes feed would have named them anyway, and the run log records only a combined target count. An earlier draft credited the staleness sweep and called it the first direct evidence the sweep catches what the feed cannot; that claim is withdrawn as uncheckable from the data. corpus_fetch.py should record feed and sweep targets separately so the next such case is decidable. This is a one-time bring-up artefact, not a property of the feed, and corpus_fetch.py now warns when the cursor sits ahead of the newest item held (verified: it fires on the historical state, and is quiet now).
- BACKFILL COUNTS ARE NOT LIKE-FOR-LIKE ACROSS THE FETCH-STRATEGY CHANGE. Under the retired full-pull-per-issue regime every thread was re-read every issue, so backfill measured the feed alone. Under catch-up fetching it also measures SWEEP COVERAGE: an item in a thread neither the feed named nor the sweep reached is invisible however old it is. Issues #3-#10 are the former, #11 straddles (a full pull sat inside its window), #12 is the latter. Compare margins, traffic AND coverage before comparing counts. Derived record for #3-#12: 0, 1, 3, 0, 1, 0, 2, 7, 3, 6; per thousand window items 0.00, 0.60, 1.66, 0.00, 1.28, 0.00, 2.39, 2.94, 1.38, 2.17.
- THE MUTATION AUDIT RESTS ON 9,135 ITEMS -- 40.0% of the corpus, in 30.5% of threads -- against 100% at issue #11. The feed_lag block also reports items_compared = 19,641, which is every item known at the previous issue's pull and NOT what was compared; an edit is only detectable in a thread re-read since then. Read the audit as 0 edits across 9,135 verified items. Issue #11's watch item #6 pre-registered exactly this: it reported 100% only because the tooling work happened to run a full pull inside its window, and a catch-up-only issue would be far lower. '0 edited items' is correspondingly a much weaker negative this issue, and it is reported with its denominator rather than on its own.
- THE SHARED-PREFIX ASSERTION IS VIOLATED, for the second time in twelve issues and the first with a consequence. 13 of the 481 shared rolling windows moved -- indices 468-480, i.e. the LAST 13, all dated 08-23 16:23 onward, which is exactly where the 3 backfilled items inserted. One (window 478, 08-23 21:35) moved 0.1274 -> 0.1259 and crossed the forth anchor, so ISSUE #11'S PUBLISHED DIP RATE REVISES FROM 16.7% TO 18.5% (9/54 -> 10/54). That sits well inside the cell's own 5-48% issue-to-issue range and changes no reading. Issue #7's violation (3 windows, 0 crossings) was the first. The assertion is doing its job: it detected an insertion the pipeline would otherwise have absorbed silently.
- THE CPU STAGE IS ~300x FASTER AND THE REGISTER SERIES IS BIT-IDENTICAL. zstd_curve.compute_metrics was rebuilding a level-19 zstd dictionary over the ENTIRE accumulated history once per 25-item bucket -- the quadratic term issue #11 flagged, ~55 min at 19,334 items -- to produce cond_full, a column no weather issue has ever read. The weather caller now requests only self and cond_win, and reuses the previous issue's rows for the unchanged prefix. Verified neutral by re-running issue #11 pinned to its published pull_at: all 18 per-day values, the whole-corpus figure, the corpus block and the churn signature reproduced exactly. 48 s cold, 11 s with the cache warm. Both reused columns are prefix-stable. So, in fact, is cond_full -- its dictionary is the history before the bucket -- and it is dropped for COST, not correctness; an earlier draft claimed it depended on later items, which is true only of cond_shuf, and that claim is corrected. cond_shuf samples items regardless of time, including ones after the item being scored, so requesting it alongside reuse raises rather than silently returning wrong numbers. The cache detected this issue's mid-stream backfill insertion and rewound 502 rows rather than trusting the prefix.
- THE n>=10 COHORT TEST REFUTED ITS OWN HYPOTHESIS. Issue #11 found 08-21's 71-author cohort converting at 18.3%, the lowest of the cohorts with n>=50, and pre-registered that two low cohorts in a row would be the first evidence event-recruited authors convert differently. 08-22's 258-author cohort entered at 35.3% -- the HIGHEST of the five n>=50 cohorts, and +8.7 points above the author-weighted pool at +2.49 counting SE. So the hypothesis is not supported, and 08-21's low cohort is the outlier rather than the pattern. The published N=3 cell moved 30.9 -> 31.3; per-cohort identity across the boundary HOLDS at all three horizons. 08-21 also entered N=4 at 29.6%, moving that cell 37.6 -> 36.9.
- Both allocation parses are published; the STRICT series remains the currency, as adopted at issue #8. Coverage is 21,959/22,107 (99.3%); all 148 uncovered items return a known WORLD phrasing and none resolved on retry, so the failure is one-sided for a seventh consecutive issue and the strict series is an upper bound on venue share.
- Allocation currency. Venue share is the Qwen binary classifier. The LEVEL carries the allocation study's 0.31-0.71 specification range; kappa(Qwen, Gemma) is 0.4278 on this pool. The TREND is the cleaner object.
- The lemmy reference is FROZEN: a fixed 2023 corpus read from results/lemmy_baseline, not re-measured per issue. Platform share 0.4665 [0.4515, 0.4853]; corrected point 0.4660. The comparator's frame biases toward the square reading LOW (55.7% meta-tier).
- THE UNCONTROLLED FIXED-SPAN CELL ROSE THIS ISSUE FOR A REASON THAT IS STILL NOT CONCENTRATION. 5-day dominance went 52.1 -> 66.8 and 7-day 61.3 -> 71.0, while the incumbent-only rows read 93.3 -> 94.1 and 95.8 -> 94.5. The rise is 08-22's 258 arrivals having now been present long enough to qualify as core (>=3 active days) instead of diluting the denominator -- the same expanding-opportunity mechanism, running the other way. Read the incumbent-only rows.
- ISSUE #11'S PRE-REGISTERED CONCENTRATION RULE DOES NOT FIRE, and correctly so. It required a move of more than 3.0 points in the incumbent-only 5-day cell ON A DAY WITH FEWER THAN 100 ARRIVALS. The move was +0.8 (93.3 -> 94.1) and the day carried 220 arrivals, so neither arm is satisfied. The incumbent-only 5-day series now reads 91.3, 91.4, 93.6, 93.6, 94.3, 93.2, 93.3, 94.1 across issues #5-#12, a range of 2.9 points.
- THE DAY-WINDOW CELLS CARRY AN EXPANDING-SPAN CONFOUND: 'core' means active on >=3 calendar days over however long the corpus happens to be, so each issue gives every cohort another day to qualify AND adds a cohort to the average. core_n went 244 -> 343 and dominance 77.7 -> 81.8 this issue; both are reported, not read.
- NEWCOMER CELLS MOVED OUTSIDE ISSUE #11'S BANDS, which is the first detectable change in this cell. Per-issue parity reads 1.067 [1.048, 1.082] and union 1.050 [1.026, 1.074] on 901 newcomer items, where issue #11 read 1.011 [0.978, 1.044] and 1.017 [0.997, 1.046] on 389 and both spanned 1. Issue #11's point estimates sit OUTSIDE this issue's bands and vice versa, so unlike the #10/#11 comparison this is a move the instrument can see rather than a precision change. The pooled cell agrees in direction (parity 1.033 -> 1.055). Caveat: m rose 311 -> 720, and a cell that has moved once is not a trend.
- The nearest-incumbent cell excludes 0 for a SIXTH consecutive issue: delta 0.0127 [0.0086, 0.0177], p = 0.000, against issue #11's 0.0077 at p = 0.04. Pooled 0.0104 [0.0069, 0.0145], p = 0.000. The pooled window shares 62.2% of its items with issue #11's (4,552 of 7,322), so consecutive pooled points remain dependent and are not a trend.
- WINDOW-CELL PRECISION IS COMPARABLE ACROSS #10/#11/#12: all three hit the m=1500 draw cap. ISSUE #3'S UPGRADE TRIGGER DOES NOT FIRE. The gte arm reads 1.066 against its <1.0 bar. The decline arm needs three consecutive declines in the bge window series, which reads 1.192, 1.192, 1.207, 1.215 across #9-#12 -- two consecutive RISES, so zero declines are banked and the arm cannot complete before issue #15.
- REGISTER SET A SERIES HIGH ON THE LARGEST DAY, BY A TYPICAL STEP. 08-24 reads 0.6597 against 08-20's previous high of 0.6571; the move is +0.0054 where the median absolute day-to-day move is 0.0053. The nineteen-day span is now 0.6367-0.6597, a range of 0.0230, and the newest day sits 0.0443 below the 0.704 human band floor. Issue #11 concluded this cell is insensitive to anything the square has yet done and set the bar for a real move at more than the whole observed range; a record day moving it by exactly the median step is consistent with that.
- Accumulation statistics. The rolling halves (0.1329 -> 0.1313) and the pooled dip share (20.7%) average over history that grows each issue; the issue-local equivalents are the primary readings.
- Overlapping-window moves are not independent confirmations. Consecutive trailing 5-day allocation means share 4 of 5 days; consecutive fixed-span structure cells share 6 of 7 (and 4 of 5) span days. No significance is attached to either series' run of moves.
- Retired series. core_n (issue #5); the fixed-horizon permeability running mean (#6); the fixed-span permeability row (#7); issue #5's three-day allocation rule (#8, confirmed at #10); the n>=5 per-cohort conversion trend (#10); and issue #10's gap-based incumbent-allocation branch (#11, withdrawn as ill-posed).
- Single-normalizer / bge-only cells. The rolling series and all newcomer cells are Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone. bge is the named embedder for issue #3's window-decline trigger, as declared at issue #9.
- Activity-clock signatures compare at matched item volume over the anchors' FULL histories and are reported, not read: the move tracks arrivals, the same recruitment confound demonstrated for the fixed-span cells. These are NOT 'young phase' comparisons.
- A per-author daily cap of 20 COMMENTS is a platform rule, verified again this issue. Day volume is therefore active authors times an intensity bounded by ~21; 08-24 ran 489 active authors at 5.66 items each, so the record day came from recruiting, not from anyone posting harder.
- The claimify batch is 8 for a fourth consecutive issue. 08-21 through 08-24 are all downstream of batch-8 claims; comparisons among them do not span the instrument change, comparisons against an EARLIER day still do.
- Identity != operator (permanent): author identities are forum identities, not distinct operators; concentration readings are about identities. The influx profile's model-label column uses the platform's own label and is not an author clustering.
