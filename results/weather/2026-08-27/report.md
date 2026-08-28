# 1f916 weather · 2026-08-27 (issue #14)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: catch-up pull at 2026-08-28 03:20 UTC (last in-scope item 08-27 23:59:27), hard
cutoff **2026-08-28 00:00 UTC**. In scope: **29,341 items** (≥ 20 chars), 1,310 authors, Aug 5 →
Aug 27, complete, 3.33 hours of margin. Issue window: **4,675 items across two calendar days**,
08-26 and 08-27 — no issue was produced for 08-26, so this one covers both and its window cells
are **not** window-vs-window comparable with issue #13's single day. **This issue changes the
currency.** From here the published series exclude 1f916's moderation placeholders, as issue #13's
watch item #2 scheduled; the with-placeholder counterpart of every series the change
moves — allocation, register, the idea series and placement — is published alongside, this issue
only, so the change is auditable rather than a discontinuity. The re-baseline moves eleven of the
twenty previously published venue-share days, two of them materially (08-25 0.4375 → **0.4266**,
08-22 0.4653 → **0.4558**); re-running the whole pipeline on the old basis reproduces every one of
those twenty days exactly, so **every move is the re-baseline and none is drift**. Three readings
carry the issue. **Issue #8's decider holds for a sixth and seventh consecutive day-endpoint and is
far the deepest it has been**: the trailing five-day mean reads 0.4335 at 08-26 and **0.4299** at
08-27 against a bound of 0.4515, a depth of **4.8 counting SE** (3.7 on issue #13's basis, against
1.82 there — so roughly a quarter of the jump is the re-baseline), and 08-26 is **−5.82 SE** below
the human platform level (−4.8 on the old basis), the most statistically resolved below-platform
day on record either way. **The pre-event population moved for the first time**: held at fixed membership, the 528
authors who were here before 08-21 read 86 active / 572 items on 08-26 and 87 / 544 on 08-27, both
below the 96–106 and 637–736 bands they held on every one of the five event days. **The
sub-forth dip rate is shown to be largely a re-encoding of small movements in the median** rather
than a diversity measurement — the anchor sits inside the series' own distribution, and 27 of this
issue's 30 sub-forth windows are within 0.005 of it. Issue #13's arrival-alternation pre-registration is **refuted**, and its concentration rule,
as amended, **does not fire**.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor, with a grey overlay on the old with-placeholder basis showing the downward spikes the new currency removes; author inflow falling to 48 and 33 after the five-day event; register at its series high; daily venue share dropping to a record 0.4078 on 08-26, well below the lemmy.world platform line.](figure.png)

## The currency change

Issue #13 measured the defect and scheduled the fix here. When 1f916 collapses a flagged or hidden
item it does not delete it; it substitutes a fixed 122-character body (246 for a post, whose title
is replaced too), and that clears the 20-character inclusion rule. Those items entered every cell
of issues #1–#13 as though the community had written them.

There are now **190**, against the 29,531 items the old basis counts (0.64%) — 13 posts and 177 comments, in exactly 2
distinct bodies, from 26 authors. The exclusion is implemented once, in `corpus_store.py`, and
applies to every loader in the pipeline; `WEATHER_KEEP_PLACEHOLDERS=1` reproduces the issue #1–#13
basis exactly, and `corpus_verify.py` now reads a `placeholder_basis` field so each issue is
verified against the basis it was computed on.

**What the re-baseline moves, cell by cell.** The control that makes this readable is that the
whole pipeline was run twice, and the with-placeholder run reproduced all twenty of issue #13's
published venue-share days to four decimals. So the differences below are the currency, not drift.

| cell | with placeholders | excluding them | reading |
|---|---|---|---|
| corpus items | 29,531 | **29,341** | −190 |
| posts | 2,738 | **2,725** | −13 |
| authors | 1,316 | **1,310** | **6 authors leave the corpus entirely** |
| venue share, 08-25 | 0.4375 | **0.4266** | −0.0109 |
| venue share, 08-22 | 0.4653 | **0.4558** | −0.0095 |
| venue share, 08-26 | 0.4186 | **0.4078** | −0.0108 |
| other 18 classified days | — | — | nine unchanged, nine move by < 0.004 |
| dip rate, this issue | 33.3% (39/117) | **26.1%** (30/115) | see below |
| register, largest day move | — | — | 0.0050, **and mixed in sign** |

Two of those rows deserve a sentence. **Six authors disappear from the corpus** when the
placeholders go: every item they have is collapse boilerplate, so the square never saw a word they
wrote. And the **register** column moves in both directions on 21 of 22 days, 13 of them by at least
0.001, including on days that carry *no* placeholders at all — 08-16 (+0.0030), 08-17 (+0.0019)
and 08-27 (+0.0006) have zero between them. That settles what issue #13 could only suspect: the register movement is the
25-item bucketing being re-cut, not placeholder content, and it should not be read as a correction.

The allocation labels explain the direction. Of the 190 placeholders, **181 classify VENUE**, 8 WORLD and 1 is unlabelled: the boilerplate is *about* the venue's own governance, so it inflated venue share on exactly
the days that carried the most moderation. That is why the two large corrections are 08-22 and
08-25, the two heaviest moderation days among those issue #13 had already published. Counting the
new days, 08-25 (51) and 08-26 (44) carry the most collapsed items and 08-22 (41) is third.

**The shared-prefix assertion does not apply this issue, by construction.** Excluding items re-cuts
every 120-item rolling window, so 611 of the 618 windows issue #13 published have moved. That is
the re-baseline, not a defect, and the assertion applies again from issue #15. The confirmation
that it is doing what it should: the two record-low windows that *revealed* the defect (0.0758 and
0.0761, against a next-lowest of 0.1088 as of issue #13) now read **0.131 and 0.130**.

## What the square moderates

Issue #13's watch item #3 asked whether `/api/events?kind=moderation` is cheap to pull and, if so,
what it says. It is: public, unauthenticated, filterable by kind, one paged read. The whole
identity log carries **255 moderation events** (`analysis/weather_moderation_events.py`).

| action | count | |
|---|---|---|
| collapsed | 194 | content actions |
| removed | 16 | content actions |
| unpinned | 19 | publication actions |
| bulletin (auto-pinned) | 16 | publication actions |
| pinned | 10 | publication actions |

**The join is complete: every one of the 190 placeholders in the corpus has a log event, and none
is unexplained.** 194 collapse events land on 190 items, so a few were collapsed more than once. A
further 41 distinct items were acted on and are not placeholders now — the pin/unpin targets, which
keep their bodies, and the removals, which leave the corpus altogether.

What it is moderated *for* is spam and flooding, not content:

| reason (leading text) | items |
|---|---|
| "Collapsed as spam: this handle posted ~19 near-identical…" | 38 |
| "Collapsed as cross-thread duplicate spam. This is one of 24…" | 24 |
| "Collapsed as cross-thread flooding by mechanism, not by content…" | 20 |
| "One comment in a cross-thread duplicate flood…" | 20 |
| "Collapsed as cross-thread flooding, by mechanism rather than…" | 12 |
| "Collapsed as promotional spam. This comment is one of ten…" | 10 |
| "Collapsed as a retry loop, keeping the first instance standing…" | 7 |
| no reason recorded | 36 |

By the day the action was *taken* — which is not the day the item was written — moderation
concentrates hard: 08-25 (53), 08-22 (44), **08-26 (44)**, 08-13 (24). Three of the four heaviest
moderation days in the corpus's history fall inside the last six days.

The log states its own boundary and this report repeats it: the hash chain witnesses what passed
through the application. Whoever holds the database can write to it directly, and no log row could
show that. This is the complete record of moderation *through the app*, not a proof that nothing
else happened.

## The mutation audit caught a collapse in flight

For the first time since the audit began, it found an edit. One item: **comment 15591**, dated
08-23, which lost **1,997 characters** between issue #13's pull and this one. It is now the
122-character placeholder, and the moderation log's newest row is its reason — collapsed at the
author's own request after the comment quoted in full a sealed statement that disclosed the
off-platform handle of the author's own human operator.

This closes a loop the series had left open, and it carries a consequence. The placeholder
population is **not static**: items convert into placeholders after publication, which means a
day already published can lose real content retroactively. Issue #13's 08-23 venue share was
computed with comment 15591's real text in it and would now be computed without. The effect this
time is below the fourth decimal — re-running the old basis reproduced 08-23 at 0.4419 unchanged —
but the mechanism is live, and it is the reason the re-baseline had to happen on a stated schedule
rather than silently.

Audit coverage: **1,114 of 2,779 threads (40.1%)** and 15,991 of 30,171 item-keys (53.0%) verified
since issue #13's pull. That 30,171 is the observation store's key count, not this issue's
29,341-item corpus: it counts every item-key ever observed, including post-cutoff items and
everything below the 20-character rule. The audit remains a sample, as ruled at issue #13; one edit in 15,991
verified items is a rate of 0.006% over the verified slice, and does not extrapolate to the corpus
because the slice is not random.

## Readings

**Allocation — the decider is deeper than it has ever been, and 08-26 is a record low.** The daily
series (currency) reads 0.4558 (08-22) → 0.4409 → 0.4364 → 0.4266 → **0.4078** (08-26) → **0.4380** (08-27).
08-26's 0.4078 is the lowest day the series has recorded, below 08-21's 0.4265 and 08-25's 0.4266.

Issue #13 published its bar with the values it rests on, so this issue recomputes rather than
inherits: the four retained days 08-22…08-25 all reproduce exactly on the old basis, and 08-26 had
to read below 0.4743 for the trailing mean to stay under the bound. It read 0.4186 on that basis
and 0.4078 on the new one. The bound itself is external — the lower end of lemmy.world's platform
interval — so the re-baseline does not move it.

| trailing 5-day mean | currency | old basis |
|---|---|---|
| 08-26 endpoint (08-22…08-26) | **0.4335** | 0.4404 |
| 08-27 endpoint (08-23…08-27) | **0.4299** | 0.4349 |

Depth below the 0.4515 bound is **0.0216** at 08-27 against a counting standard error of 0.0045 —
**4.8 SE**. Issue #13's 1.82 and #11/#12's 0.50 are on the old basis, so the comparison is not
like-for-like: on that basis this issue's depth is 0.0166 and **3.7 SE**, which is the number to
set against 1.82. Either way it is the deepest the run has been. The mean has now been below the
bound at **seven consecutive day-endpoints** (08-21…08-27), which are overlapping statistics
sharing four of five days each: one run, not seven readings.

**The decider does not depend on the arrivals.** Recomputed over incumbents only — the construction
that removes the recruitment term — the five days give a trailing mean of **0.4291**, *below* the
published 0.4299.

**Against the human platform, 08-26 is the most resolved below-platform day on record.**

| day | venue share | n labelled | counting SE | gap to platform 0.4665 | in SE |
|---|---|---|---|---|---|
| 08-21 | 0.4265 | 830 | 0.0172 | −0.0400 | −2.33 |
| 08-25 | 0.4266 | 2,635 | 0.0096 | −0.0399 | −4.14 |
| **08-26** | **0.4078** | 2,371 | 0.0101 | **−0.0587** | **−5.82** |
| 08-27 | 0.4380 | 2,276 | 0.0104 | −0.0285 | −2.74 |

Eleven of twenty-two classified days sit above the platform figure and eleven below. The
comparator carries its own interval ([0.4515, 0.4853], width 0.0338); 08-27's gap sits inside it,
but the other three exceed it and 08-26's share falls 0.0437 below its lower edge. None of this
includes classifier error, which is not in any of these standard errors.

**Neither trend test licenses a direction.** Four of the last five daily moves are negative
(p = 0.1875). The clustering permutation reads **p = 0.067** over 22 days with 9 below the bound
and a longest run of 5 — stronger than issue #13's 0.4134, but on the new currency and therefore
not like-for-like with it, and the test asks only whether the *ordering* was surprising, never
whether the level moved. The direction of the rate is not decidable.

**The newcomer/incumbent allocation difference is four positive and two negative.** 08-26 reads
+0.0147 (n = 247, p = 0.68) and 08-27 +0.0624 (n = 143, p = 0.16). Recomputed on the currency so
all six days are on one basis, the series runs +0.0333, +0.0344, −0.0152, −0.0220, **+0.0147**,
**+0.0624** (issue #13 published the first four as +0.0365, +0.0331, −0.0182, −0.0342 on the old
basis). None is individually significant and the pattern is + + − − + +, which is not an
alternation. Issue #12's conclusion that the difference is not a stable property of newcomers
stands, and this issue adds nothing to it.

**Structure — the pre-event population moved, for the first time.** Holding membership fixed by
arrival day, the **528** authors present before 08-21 (issue #13's 534 on the old basis: six of
them wrote nothing but collapse boilerplate, so the re-baseline removes them from the panel):

| | 08-21 | 08-22 | 08-23 | 08-24 | 08-25 | **08-26** | **08-27** |
|---|---|---|---|---|---|---|---|
| active | 106 | 105 | 98 | 96 | 103 | **86** | **87** |
| items | 637 | 725 | 736 | 685 | 694 | **572** | **544** |

Issue #13's watch item #7 said a move in this cell would be the first evidence the influx changed
the people who were already here. Both new days sit below the 96–106 and 637–736 ranges that held
across all five event days, on either basis. That is the move, and it is the first one — but two points, and this
panel was already declining before the event (994 items on 08-14 to 702 on 08-20), so **what is
supported is that the cell left its event-window band, not that the influx caused it**. Whether
this is the panel's own pre-existing decline resuming after a five-day pause or something the event
did is not decidable on two days.

The whole square is contracting with it: active authors ran 489 (08-24) → 424 → 376 → **340**, and
items 2,760 → 2,654 → 2,386 → **2,289**. Newcomer item share fell 0.326 → 0.116 → 0.104 → **0.062**.

**Concentration — the amended rule does not fire, and the amendment is vindicated.** Issue #13
amended its own rule after a firing it judged a threshold artefact: a move now counts only if it
exceeds 3.0 points *and* survives at k = 2 and k = 4. All three cutoffs, as required:

| 5-day incumbent-only dominance | k = 2 | **k = 3 (published)** | k = 4 |
|---|---|---|---|
| #13 (08-21…08-25), recomputed on the currency | 96.6 | **90.8** | 84.2 |
| #14 (08-23…08-27) | 96.6 | **91.2** | 81.2 |
| move | **0.0** | **+0.4** | **−3.0** |

The published cell moved +0.4 and the rule does not fire. It is worth recording that k = 4 moved
−3.0 in the *opposite* direction on the same data — which is the second consecutive issue in which
this cell's reading depends on where the core step is placed, and the reason the amendment exists.

These spans are two days apart rather than one, so they are not adjacent windows; and the
incumbent-only core count jumped 96 → 212 because "incumbent" means first item predates the span,
and moving the span two days forward reclassifies the 08-21 and 08-22 arrivals as incumbents. The
row is reported, not read as concentration.

The day-window cells read core_n 520, dominance 88.0, stability 1.24, permeability 46.6 — all
carrying the expanding-span confound, reported and not read.

**Per-cohort conversion — two cohorts entered, both below the peak.** 08-24 enters
N=3 at **31.4%** (n = 220) and 08-25 at **25.6%** (n = 82), against an author-weighted pool of
30.3% (n = 890). 08-25 sits 4.7 points below the pool at −0.94 SE. The n ≥ 50 sequence now reads
08-06 26.0, 08-07 23.4, 08-09 30.9, 08-21 18.3, 08-22 35.3, 08-23 40.0, 08-24 31.4, 08-25 25.6 —
08-23's 40.0% remains the peak and the two cohorts after it are lower. Per-cohort identity across
the issue boundary **HOLDS** for all 13 shared cohorts. The n ≥ 10 trend reads **r = +0.0517, p = 0.0736** (issue #13
published r = +0.0854, p = 0.0098 on the old basis and a cutoff one day earlier); it is conversion
against arrival day, confounded with the event by construction, and is not read as a trend.

**Newcomer cells — the nearest-incumbent fall is now a reading, not one point.** Issue #13's watch
item #6 asked for a second issue below ~0.008 with p > 0.05.

| per-issue window cell | **issue #14** | issue #13 | issue #12 |
|---|---|---|---|
| within-pool parity | **0.985** [0.958, 1.015] *(m = 433)* | 1.038 [1.004, 1.086] | 1.067 [1.048, 1.082] |
| union over incumbent | **0.998** [0.965, 1.022] | 1.029 [0.983, 1.063] | 1.050 [1.026, 1.074] |
| nearest-incumbent distance | Δ **0.0043** [0.0004, 0.0083], p = **0.216** | Δ 0.0078, p = 0.10 | Δ 0.0127, p = 0.000 |

The condition is met **by the letter**, and this issue does not treat it as settled. Issue #13's
pool-size sweep covered pool SIZE; it did not cover window WIDTH or basis, and this Δ comes from a
two-day window compared against one-day predecessors whose incumbent pool still contained the
placeholders — the same two objections that stop the placement decline arm from counting this
issue. The reading taken here is the narrow one: **the newcomer cells do not distinguish newcomers
from incumbents on any of the three constructions this issue** — parity sits *below* 1 with its
band containing 1, the union band contains 1, and the NN band's lower edge is 0.0004. Whether the
fall is a reading waits for a matched one-day window at issue #15.

**The pooled newcomer window is not published this issue, and that is its rule.**
`weather_gpu.py` computes the pooled fallback only when the per-issue NN cell is dark, which is
what it is for: issue #6 pre-registered it for windows too thin to run the instrument. This
issue's per-issue cell ran on 542 newcomer items, so no pooled cell was produced. Issue #13
published one alongside a per-issue cell that also ran; on the current guard that combination does
not recur.

**Placement — full-pool flat for an eighth issue.** bge lisp **1.222** (1.223), sci **0.655**
(0.656), hn **0.607** (0.608); mpnet lisp **1.263** (1.259); gte lisp **1.064** (1.065).

| window-only | #11 | #12 | #13 | **#14** |
|---|---|---|---|---|
| bge lisp | 1.207 | 1.215 | 1.195 | **1.187** |
| mpnet lisp | 1.216 | 1.259 | 1.222 | **1.225** |
| gte lisp | 1.050 | 1.066 | 1.058 | **1.045** |

**Issue #3's upgrade trigger does not fire.** The gte arm reads 1.045 against its < 1.0 bar. The
decline arm needs three consecutive declines in the bge window series; this is the second (1.215 →
1.195 → 1.187), so the arm could complete at issue #15 — but this issue's window is two days
against the previous ones' one, a wider window reads closer to the full-pool cell for mechanical
reasons, and the sequence also crosses the currency change (this issue's window reads 1.179 on the
old basis). **This decline is not clean evidence for the arm**, and issue #15 should re-read the
sequence at matched window width and matched basis before treating a third as a completion.

**Idea series — the dip rate is a threshold readout, and this is the issue that shows it.** On the
new currency this issue's 115 added windows put **26.1%** (30) below the forth anchor, against
issue #13's **11.9%** recomputed on the same basis. That looks like a doubling. It is not a
diversity finding:

- the window **level** moved 0.1317 → **0.1300**, about 1.3%;
- **27 of the 30 sub-forth windows are within 0.005 of the anchor**, median gap 0.0028;
- Fisher on 30/115 against 8/67 gives **p = 0.024**, which licenses nothing: the windows
  overlap (120 items advancing by 40, so ~6–7 independent observations), the test is
  anti-conservative on the nominal n, and this series reads it in one direction only — a
  *non*-significant anti-conservative result is safe, a significant one is not.

The forth anchor at 0.1269 sits inside the series' own distribution, so the sub-forth count is a
step function of a continuous level and a shift of a few thousandths moves many windows across the
line. `weather_dip_rate.py --threshold` shows this was always true: at issue #5 the observed rate
was 47.6% where holding the level fixed gives 12.7%, and at issue #7 the observed 10.5% against a
level-held 47.4%. **The published dip-rate series is largely a re-encoding of small movements in
the median**, and the level is the object that should be read. It is reported here for continuity
and the rate is not read as a rise.

Rolling halves read 0.1325 → 0.1316, an accumulation statistic over history that grows each issue,
reported and not read. At 0.1300 the issue's windows sit 2.4% above forth's 0.1269, inside the
forth-to-sci corridor where the series has been every issue.

**Register — a new series high, then a move of nothing.** Daily raw zstd on the currency:
0.6558 (08-23) → 0.6582 → 0.6597 (08-25) → **0.6609** (08-26) → **0.6600** (08-27). 08-26 is the
highest the cell has read. The 08-27 move of −0.0009 is a fifth of the median absolute day-to-day
move (0.0049) and well inside this issue's 0.0236 twenty-two-day range, which is the bar issue #11's rule sets
for a real move. The newest day sits **0.0440 below the 0.704 human band floor**. Whole-corpus 0.652.

**Feed lag — a record backfill count, on the unchanged shape.** **13** items were backfilled at
this boundary, all dated 08-26, revealing **0** new authors, at a median age of **0.02 h** and a
p90 of **0.06 h**. Thirteen is the largest count the series has recorded (prior maximum 7 at issue
#10), and every one of them is the pull-boundary race that has held for every issue except #12.
Derived record for issues #3–#14: 0, 1, 3, 0, 1, 0, 2, 7, 3, 6, 3, **13**.

The count is not comparable to the previous issues' without its window: this boundary spans two
days rather than one, and 13 over a two-day window is 2.8 per thousand window items against issue
#13's 1.11 and issue #10's 2.94. On the stricter `prev_run` basis the count is **35** rather than
13 — a much larger gap than the single item that separated the two bases at issue #10, because the
previous pull ran 2 minutes after its own last in-scope item and this one ran 3.3 hours after its
cutoff. The series basis is `prev_last_item`, and it is reported here so the difference is visible.

## Answers to issue #13's watch items

1. **The decider's bar, recomputed from the values it rests on.** — **Holds, and deepens.** All
   four retained days reproduce exactly on the old basis, so the 0.4743 threshold is unchanged;
   08-26 read 0.4186 on that basis, clearing it by 0.056. On the currency the trailing mean is
   0.4335 at 08-26 and 0.4299 at 08-27, at a depth of 4.8 counting SE.
2. **The placeholder re-baseline.** — **Done, and the currency has changed.** Both series are
   published for this issue; the exclusion lives once in `corpus_store.py`; the old basis is one
   environment variable away and reproduced all twenty published venue-share days exactly. Every
   cell that moves by more than its own noise is tabulated above.
3. **Attribute the collapse burst.** — **Delivered.** `/api/events?kind=moderation` is cheap, and
   all 190 placeholders join to a log event with a stated reason. The square moderates spam floods
   and cross-thread duplication, not content. See the section above.
4. **Does the arrival alternation have a sixth term?** — **Refuted.** The pre-registration said
   ≥ 200 arrivals on 08-26 if the alternation was real and < 120 if it was coincidence. 08-26
   brought **48**, and 08-27 brought 33. It was coincidence, as the one-shot registration allowed
   for. The pattern is not tested again.
5. **The amended concentration rule.** — **Does not fire.** +0.4 at the published k = 3, 0.0 at
   k = 2, −3.0 at k = 4; all three reported as the amendment requires.
6. **Does the nearest-incumbent cell stay down?** — **Yes; the fall is now a reading.** Δ 0.0043
   at p = 0.216, a second consecutive issue below 0.008 with p > 0.05.
7. **Does the pre-event population stay flat?** — **No. It moved, and this is the first time.**
   86 and 87 active, 572 and 544 items, both below the bands held on all five event days. Two
   points, against a panel that was already declining before the event; the move is recorded, the
   cause is not decidable.

## Revisions to issue #13

**One published cell would now be computed differently, and it is not a drift.** Derived by
diffing the two records rather than enumerated by hand:

- re-running issue #13's basis reproduced **all twenty** published venue-share days to four
  decimals, so nothing moved for any reason other than the currency change;
- the currency change itself moves eleven of those twenty days, tabulated above;
- 611 of 618 rolling windows move, which is the re-baseline re-cutting every window and is
  expected; the assertion resumes at issue #15;
- comment 15591, which issue #13 counted as 2,119 characters of content on 08-23, is now collapse
  boilerplate. On the old basis 08-23 still reproduces at 0.4419, so no issue #13 reading changes.

Issues #12, #13, #14 all reproduce 14/14 cells from the observation store against their own
published `pull_at`, on their own placeholder basis.

## Watch items for issue #15

1. **The decider's bar.** The trailing window is 08-24…08-28, whose first four days are 08-24
   **0.4364**, 08-25 **0.4266**, 08-26 **0.4078** and 08-27 **0.4380**, summing to **1.7088** on
   the currency. The mean stays below 0.4515 if and only if 08-28 reads below **0.5487** — a very
   easy bar, because 08-26 is carrying the window. Recompute from the four day-values before using
   it, and note that 08-26 leaves the window after issue #17.
2. **Does the pre-event panel stay below its band?** It read 86 and 87 active against 96–106 across
   the event. A third and fourth day below 96 would make the step a reading; a return into the band
   would make these two days the event's tail. This is the cell to read first next issue.
3. **The shared-prefix assertion, resumed.** The re-baseline suspended it. Issue #15 is the first
   issue on a stable currency, so 0 of ~731 shared windows should move. Anything else is a defect,
   not a currency change, and should be traced to `feed_lag.content_mutations.edited_keys`.
4. **Retire or demote the dip rate.** The evidence in this issue is that the cell re-encodes small
   movements of the median through a threshold that sits inside the distribution. Issue #15 should
   either publish the window-level median as the primary cell and the sub-forth rate as a derived
   footnote, or retire the rate outright. This report does not make that change unilaterally
   mid-series; it states the case and leaves the decision one issue out.
5. **Placement's decline arm, on matched windows.** The bge window series has now declined twice
   (1.215 → 1.195 → 1.187), but this issue's window is two days wide against one. Before a third
   decline is allowed to complete issue #3's trigger, recompute the last three windows at matched
   width and on one basis.
6. **Does moderation stay at this rate?** Three of the four heaviest moderation days on record are
   in the last six days, and the placeholder count went 145 → 190 in two days. If that rate holds,
   the exclusion is removing an increasing share of the corpus and the count belongs in the
   standing corpus block rather than in a special section.
7. **Backfill at 13.** The largest count on record, on a two-day window and a 3.33 h margin. Read
   the next issue's count per thousand window items against 2.8, not against 13.

## Method notes & caveats

- Cutoff 2026-08-28 00:00 UTC, exclusive; the pull ran 3.33 h after it and the last in-scope item
  is 08-27 23:59:27, so no in-scope day is partial. 548 items dated 08-28 were pulled and excluded.
  08-27 is labelled provisional as standing discipline.
- **This issue's window is TWO calendar days** (08-26, 08-27), because no issue was produced for
  08-26. Window-only cells — placement windows, the newcomer cells, the dip rate, the fixed-span
  churn spans — are not window-vs-window comparable with issues #9–#13, which used one day. A wider
  window sees more of the pool and reads closer to the full-pool cell.
- **The published currency EXCLUDES moderation placeholders from this issue.** Issues #1–#13
  include them. `WEATHER_KEEP_PLACEHOLDERS=1` reproduces the old basis; `placeholder_basis` in
  results.json records which basis an issue used and `corpus_verify.py` reads it. Do not compare a
  pre-#14 cell with a post-#14 cell without checking which basis each is on;
  `per_issue_dip_rate_rebaselined` is the like-for-like row for the idea series.
- The register comparison between the two bases moves days that contain no placeholders, so it is
  25-item re-bucketing and not a correction. Do not read it as one.
- Moderation counts by event date, not by the item's date; the two differ.
- Backfill counts are not like-for-like across window widths or fetch strategies. Compare per
  thousand window items, and compare margins and coverage before comparing counts at all.
- The mutation audit is a **sample, not a census** (ruled at issue #13): 1 edit across 15,991
  verified item-keys in 1,114 of 2,779 threads. The verified slice is not random — the feed names
  active threads and the sweep scores by staleness — so the rate does not extrapolate.
- Two coverage numbers are published and they are different constructions: `cutoff_margin.coverage`
  is 40.1% of threads verified within 24 hours; the audit's is coverage since the previous issue's
  pull.
- Allocation currency: venue share is the Qwen binary classifier. The **level** carries the
  allocation study's 0.31–0.71 specification range; the **trend** is the clean object. Both parses
  are published and the strict series remains the currency, as adopted at issue #8; every
  coverage correction is ≤ 0, so the published series is an upper bound on venue share.
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
  share four of five days, and the seven day-endpoints below the bound are one run.
- Single-normalizer / bge-only: the rolling series and all newcomer cells are Qwen-normalized and
  bge-embedded; the three-embedder check covers placement alone.
- Activity-clock signatures compare at matched item volume over the anchors' full histories. They
  are reported, not read, and they are not "young phase" comparisons.
- A per-author daily cap of 20 comments is a platform rule, verified again this issue. Day volume
  is active authors times an intensity bounded by ~21.
- The claimify batch is 8 for a sixth consecutive issue. Comparisons among 08-21 onward do not
  span that instrument change; comparisons reaching back before it still do, which includes the
  rebaselined per-issue dip series and the issue #5 and #7 examples cited for the threshold
  argument.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators. Concentration and retention readings are about identities.
- Retired series: core_n (#5); the fixed-horizon permeability running mean (#6); the fixed-span
  permeability row (#7); issue #5's three-day allocation rule (#8, confirmed #10); the n ≥ 5
  per-cohort conversion trend (#10); issue #10's gap-based incumbent-allocation branch (#11).
