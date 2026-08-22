# 1f916 weather · 2026-08-20 (issue #8)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: full pull at 2026-08-21 23:42 UTC (last in-scope item 08-20 23:47:49), hard cutoff
**2026-08-21 00:00 UTC**. In scope: **13,949 items** (≥ 20 chars), 534 authors, Aug 5 → Aug 20
(complete, 23.7 hours of margin — this issue ran a day late). Issue window (since issue #7's last
pulled item, 08-20 02:45): **511 items** inside one calendar day. The headline is a reversal.
Issue #7 reported that issue #5's pre-registered three-day rule had fired and that below-platform
self-allocation was a **sustained** finding; one day later the series is back above the platform
line, and by issue #7's own watch item that makes 08-17..08-19 **a three-day dip and the rule a
false positive**. So this issue retires the rule, replaces it with one that can only fire if the
level stays down, and adopts the corrected parse issue #7 pre-registered — which reproduces issue
#7's predicted numbers **exactly**, on two independent code paths, and moves the comparator from a
worst-case bound to an exact figure. Two other pre-registered triggers fired: inflow's second
consecutive day at or below 6, and the dip rate's second consecutive issue out of the 40s. Two
readings that were unavailable at issue #7 came back: the controlled dominance widths agree again,
and the per-cohort trend test can update again now that its cohort floor has been decided.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow at 5 per day for a second consecutive day; register climbing to a series high still well below the human band floor; daily venue share dipping below the lemmy.world platform line for three days and returning above it, drawn under both the strict and corrected parses.](figure.png)

## Readings

**Allocation — the excursion reversed, and the rule that called it sustained is retired.** The
series ran 0.4720 (08-16) → 0.4484 (08-17) → 0.4508 (08-18) → 0.4367 (08-19) → **0.4699** (08-20).
That is back inside the 0.456–0.548 band that held for nine days through issue #4, back above the
[lemmy.world](../../lemmy_baseline/report.md) platform point estimate (**0.4665**), and back
above the platform interval's 0.4515
lower bound. Issue #7's watch item #2 stated the two branches in advance: *two further days below
0.4515 make it a five-day regime; a return above 0.456 makes 08-17..08-19 a three-day dip and makes
issue #5's three-day rule a false positive worth re-examining.* **The second branch fired**, on the
first day after the threshold was declared met.

The re-examination is the substance here, because the rule was pre-registered and it still failed.
What issue #5's rule actually tests is **clustering**, not level. Three of the fifteen classified
days sit below 0.4515, and they happen to be adjacent; under an exact permutation over day order
(`analysis/weather_trend_tests.py`, `run_below`) three marked days land in a run of three in 13 of
455 arrangements, **p = 0.0286**. So the clustering is not a coincidence of ordering — but that
null is the wrong one, because a series with a downward drift places its lowest values next to each
other for free, with no regime change at all. A run rule cannot distinguish those two situations,
and this issue is the demonstration.

Two things about that replacement should be said against it rather than left for a reader to
notice. The rule is being replaced **only in the branch where it embarrassed itself** — had 08-20
come in at 0.44 it would still be standing — and the replacement is **strictly harder to fire**,
since a 5-day mean carries roughly 1/√5 of the daily noise against the same bound. That is a
ratchet toward the null, and it is a real cost of the change, not a neutral improvement. The
defence is that the re-examination was pre-registered by issue #7 rather than invented after the
fact, and that a rule which cannot tell clustering from level was not measuring the thing it was
named for. The retirement is therefore **provisional on issue #9**: if the level goes back below
the bound and stays, issue #7 was reading it correctly and this issue was the noise.

The replacement pre-registered here is a **trailing 5-day mean below the comparator's lower bound**
— a statistic that can only fire if the level stays down. The full series is 0.5189 (08-10), 0.5102,
0.4961, 0.4888, **0.4927** (08-14, the one rise), 0.4869, 0.4804, 0.4789, 0.4713, 0.4589,
**0.4556** (08-20): falling on nine of its ten moves and **never once below 0.4515**. It would not
have produced issue #7's false positive.

That series is *consistent with* a slow downward drift, and this issue does not claim more than
that. **No test here separates drift from noise over the full fifteen days.** No significance
attaches to the nine-of-ten fall — consecutive trailing means share four of their five days, so
those moves are mechanically dependent — and the within-window daily direction remains **not
decidable**: three of the last five daily moves are negative, which fair-coin signs produce half
the time (p = 0.5). What can be said is narrower than "the level is falling": the trailing mean has
gone 0.5189 → 0.4556 over eleven days without once crossing the bound, and the three-day excursion
sat inside that range rather than stepping below it.

**Where the day actually sits is parity, not comfort.** 08-20 reads **1.007×** the platform point
estimate. That is above it, and it is above it by less than one part in a hundred. Eleven of fifteen
classified days now sit above the platform figure and four below.

**The corrected parse is adopted, and it reproduces issue #7's prediction exactly.** Issue #7
characterised the classifier's failure mode — every unparseable answer is the verbatim string
`SUBJECT MATTER`, the second branch of the question the prompt itself asks — published the corrected
14-day series in advance, and pre-registered adopting it here. Issue #8 does, in
`analysis/weather_alloc_parse.py`, now the single source of truth for the parse and imported by both
the pipeline and its audit so the two cannot diverge. All fourteen predicted days reproduce **to
four decimals**, and two independent code paths (`weather_gpu.py` and `weather_label_failures.py`)
agree bit-for-bit. The corrected series reads 0.5446 (08-06) … 0.4467 (08-17), 0.4466 (08-18),
0.4303 (08-19), **0.4672** (08-20).

Worth stating plainly: the intermediate **relaxed** parse — accept an answer that names VENUE or
WORLD anywhere — recovers **zero** of the 87 failures, because `SUBJECT MATTER` contains neither
word. That is why the corrected parse is an allowlist of *observed* strings rather than a substring
match. A new failure string has to be seen and added; matching "subject" or "world" speculatively
would be a different classifier, not a parse fix.

**The comparator is now corrected exactly, not bounded.** Correcting one side of a comparison only
would be rigged, and issue #7 could only bound the other side because it did not have the
comparator's discarded answers. `analysis/weather_lemmy_recover.py` recovers them without
re-measuring the frozen corpus: the 55,153 published V/W labels are read and never recomputed, and
only the 70 unlabelled items are put back through the frozen prompt — of which **63 have valid
claims** (the other 7 are invalid claims, excluded from the denominator on both sides and therefore
not unparsed answers at all). The comparator's failure mode is **the same and equally one-sided**:
62 of 63 return `SUBJECT MATTER`, none return anything VENUE-parseable. The platform figure moves
0.4665 → **0.4660**, against issue #7's worst-case bound of 0.4659.

**One discrepancy has to be shown rather than absorbed, because the figure is being sold as
exact.** The frozen baseline publishes **55,152** classified items; the label cache it was computed
from carries **55,153** V/W labels. The difference is one item, and it is not invalid claims —
every labelled item in the cache has a valid claim. Its provenance is inside the baseline's own
pipeline and is not chased here. Nothing published turns on it: both denominators give 0.4665 to
four decimals and both corrections give 0.4660. The corrected figure above uses the cache's 55,153,
and `lemmy_comparator_corrected` in results.json now carries both numbers and their difference. Corrected on both sides, 08-20
reads 0.4672 against 0.4660, i.e. **1.003** — the same conclusion under either currency, and the
same 11 of 15 days above the line.

One recovered answer is `COMMUNITY`, which is semantically a VENUE answer. It is deliberately left
unparsed: reading it that way is a judgement about meaning, not a parse. Counting it VENUE would
move the comparator by **+0.00001** (`weather_lemmy_ref.corrected_platform`, field
`unparsed_as_venue_move`), which is four decimal places below anything the report reads.

**Level caveat unchanged**, and one bias note that now cuts the other way. The absolute number
carries the allocation study's 0.31–0.71 specification range. The comparator's 55.7% meta-tier
frame makes the human benchmark *more* self-referential than a neutral human platform would be, so
its bias runs toward the square reading **low** against it — which cut against issue #7's
below-platform finding and cuts in **favour** of this issue's at-parity reading. Both should be
held loosely for the same reason.

**Label coverage — the failure is stable and still one-sided.** The uncovered count went 72 → 83 →
**87**: the same 83 items, item for item, plus 4 new ones on 08-20. Zero of the 83 retries resolved
and `published_days_moved` is empty, which is the third issue in a row confirming that retrying is
inert under greedy decoding. Re-running the frozen prompt over all 87 returns `SUBJECT MATTER`
**87 times out of 87**. Coverage is 13,862/13,949 (**99.4%**). The published strict series remains
an upper bound on venue share, by 0.0006 to 0.0064 per day — and now the corrected series sits
beside it rather than only in prose.

**Structure — inflow's floor is now a second consecutive day, not a single point.** New authors per
day: 8 → 5 → **5**. Issue #7's watch item #3 set it out: *a second consecutive day at or below 6
makes the collapse a regime rather than a scatter; a return to 8+ means the last two issues have
been reading noise in both directions.* **The first fired.** Newcomer item-share fell again to
**0.010** (0.012), another series low. Daily item volume continued to erode: 934 → 794 → 797 → 759
→ 746 → **702** over six days, non-monotonically. Active authors **118** (121), inside the 112–123
scatter the series has held for six days. On counts this small the noise is about ±2 authors, so
"regime" here means the level has stopped bouncing back, not that a mechanism has been identified.

The published day-window cells moved as they always do — core_n 218 → 226, dominance 89.4 → 90.6,
stability 1.21 → 1.19, permeability 46.9 → **47.2** — and still carry the expanding-span confound,
so they are reported and not read.

Under the fixed-observation-span control:

| fixed span | #1 | #2 | #3 | #4 | #5 | #6 | #7 | **#8** |
|---|---|---|---|---|---|---|---|---|
| core dominance %, 7-day | 75.8 | 79.2 | 83.0 | 85.8 | 91.3 | 91.8 | 91.7 | **93.8** |
| core dominance %, 5-day | 77.1 | 79.3 | 84.3 | 86.4 | 87.6 | 88.4 | 91.0 | **93.2** |
| stability ratio, 7-day | 1.62 | 1.50 | 1.42 | 1.34 | 1.24 | 1.25 | 1.19 | **1.17** |
| stability ratio, 5-day | 1.61 | 1.51 | 1.43 | 1.35 | 1.32 | 1.32 | 1.25 | **1.22** |

**The two widths agree again, and both rose, so "core concentration is rising" is available for the
first time since issue #5.** 7-day 91.7 → 93.8 (+2.1) and 5-day 91.0 → 93.2 (+2.2) — the 7-day
cell's fall at issue #7 does not survive contact with 08-20, and the disagreement that made the
reading unavailable at issues #6 and #7 has resolved in the direction the series held before it.

**The same dependence caveat the allocation section applies to its trailing means applies here, and
it is only fair to apply it in both places.** Consecutive fixed-span cells share 6 of their 7 (and 4
of their 5) span days, so the +2.1 and +2.2 are mechanically dependent moves, not two independent
confirmations — and being "the largest agreeing move of the series" partly reflects the same day's
data counted at both widths. What carries the reading is the **eight-issue series**, which rises on
7 of 7 moves at the 5-day width and 6 of 7 at the 7-day, not this issue's single agreeing step. No
significance is attached to either, for the same overlap reason.
**Controlled stability fell at both widths** for a third consecutive issue (1.19 → 1.17, 1.25 →
1.22), which is the same story told the other way round.

The retired fixed-span permeability row reads 52.2 → 55.6 at 7 days and 54.6 → **63.7** at 5 days.
It is not read — a nine-point jump in one issue is exactly the span-relative cohort reassignment
issue #7 retired it for, and the row's continued volatility is the retirement being vindicated
rather than a finding.

**Per-cohort conversion — the floor decision is made, and the test can update again.** Issue #7's
watch item #7 required a decision rather than another carry-forward, and it was right to: at the
undisclosed n ≥ 10 floor, N=3 is **bit-identical for the third consecutive issue** (r = +0.0908,
p = 0.0444, the same 497 authors over the same 10 cohorts), and per-cohort identity HOLDS at all
three horizons. Re-reporting that as a fresh measurement is the failure mode two other cells were
retired for.

The decision taken is to **split the floor by purpose**: n ≥ 10 stays for the displayed per-cohort
table, where a percentage over six authors is noise, and the **trend test drops to n ≥ 5**, which it
can afford because it is author-level with a permutation null and does not need per-cohort
estimates to be stable. A sunset is attached: if inflow makes even n ≥ 5 cohorts unavailable, the
test retires rather than being re-reported frozen. At the new primary floor:

| horizon | cohorts | authors | r | p |
|---|---|---|---|---|
| **N=3 (primary)** | 14 | 524 | **+0.1036** | **0.0188** |
| N=4 | 13 | 516 | +0.0840 | 0.0600 |
| N=5 | 12 | 510 | +0.0953 | 0.0321 |

**This is not an establishment event, and most of what moved is the rule change.** Issue #7
reported the n ≥ 5 sensitivity as r = +0.0873, p = 0.0477; the whole move to +0.1036 is the entry of
**one 8-author cohort** (08-18, 50.0%), because the per-cohort cells are frozen and only entry can
change the statistic. That is legitimate evidence about a trend in a way that entry into a *mean*
would not be — but the late cohorts carrying the correlation hold 6 to 11 authors each (08-14 n=10,
08-15 n=11, 08-16 n=7, 08-17 n=6, 08-18 n=8), one of them converts at 14.3%, and this is three
correlated horizons of one hypothesis with no multiplicity correction. **Direction positive and
consistent; effect still not established; the cell is now capable of being wrong next issue, which
is the whole point of the change.**

**Newcomer — the per-issue cell is dark for a third issue, and the pooled cell's second point is
mostly the first point again.** The window carries **5** newcomer items against 506 incumbent, far
below the floors (m ≥ 100 Vendi, m ≥ 50 NN). The pooled window spans 08-18 04:31 → the cutoff,
**2.81 days, 145 newcomer against 1,835 incumbent**.

| pooled cell (K=3; 145 newcomer / 1,835 incumbent) | #7 | **#8** |
|---|---|---|
| within-pool parity | 0.992 [0.957, 1.018] | **1.010** [0.967, 1.071] |
| union over incumbent | 1.002 [0.975, 1.027] | **1.029** [0.988, 1.062] |
| nearest-incumbent distance, matched pools | Δ 0.0092, p = 0.036 | Δ **0.0199** [0.0116, 0.0279], p = **0.004** |

The *displaced but not diversifying* reading repeats and sharpens: newcomer claims spread
internally about as widely as incumbent claims (parity band spans 1), adding them does not raise
the incumbent pool's effective distinct content (union band spans 1), and they sit measurably
farther from the incumbent cloud than incumbents sit from each other — now by about 7% of the base
distance rather than 3%.

**Issue #7's watch item #4 required the dependence be quantified rather than asserted, and it is
large.** `weather_newcomer.pooled_overlap()` reports **1,278 of this issue's 1,980 pooled items —
64.5% — are the same items issue #7 pooled.** These are not two observations of the same quantity;
they are one observation and a two-thirds re-run of it. The Δ moving from 0.0092 to 0.0199 with
*fewer* queries (145 against 423) is not explicable as power, but with two-thirds of the data shared
it is not a trend either. One further wrinkle the overlap figure does not capture: the
newcomer/incumbent **split** is not shared even where the items are, because an author is a
newcomer relative to each window's own start, so this issue's later start reclassifies issue #7's
earlier arrivals as incumbents. **The first genuinely independent second point is issue #10.**

**Placement — full-pool flat, and the embedders disagree about the window.** Full-pool bge: lisp
**1.221** (1.229), sci **0.660** (0.657), hn **0.613** (0.611); gte lisp **1.064** (1.062) and mpnet
lisp **1.262** (1.264). Every move is far inside its own band (bge full lisp [1.199, 1.270]); the
narrowing that ran through issues #2–#6 remains stopped rather than reversed.

Window-only cells (m=408), judged against like-kind one-day windows only — issues #4 (m=774), #6
(424) and #7 (416), never issue #5's three-day one:

| one-day window, lisp | #4 | #6 | #7 | **#8** |
|---|---|---|---|---|
| bge | 1.185 | 1.200 | 1.172 | **1.186** |
| mpnet | 1.220 | 1.194 | 1.159 | **1.120** |
| gte | 1.044 | 1.051 | 1.031 | **1.029** |

**Issue #3's upgrade trigger — a third consecutive window decline, or a gte window cell below 1.0 —
fires on one embedder of three and not the other two, and the trigger never said which embedder it
reads.** On bge the series is a rise after one decline. On gte it is two small declines and the cell
sits at 1.029, with its lower bound recovering from 1.002 at issue #7 to **1.011**, so issue #7's
watch item #5 resolves *away* from parity. On **mpnet** it is a monotone decline across all four
one-day windows. A monotone run of four is one of the 24 possible orderings, so on its own it is
weak, it is weaker still after looking at three embedders, and every consecutive pair overlaps in
band. **No condition is claimed to have fired**, because reading a trigger on whichever embedder
happens to satisfy it is how a series talks itself into findings — but the trigger needs to name its
embedder before the next issue, and that is a watch item rather than a judgement call made quietly
here.

**Idea series — the dip rate stayed out of the 40s and the prefix held.** Over the **17 windows this
issue added**, the sub-forth dip rate is **11.8%** (2/17), against 10.5% (2/19) at issue #7 and
42.1% at issue #6. Issue #7's watch item #6 asked whether the collapse was real: *a second issue in
the 10s–20s says #5 and #6 were the excursion; a return to the 40s says #7 was.* **The first
fired.** 2/17 against 2/19 is Fisher two-sided p = 1.0 — indistinguishable, which here is the point,
since the question was whether #7 repeated rather than whether it moved. The new-window mean is
0.1330 (0.1335). The pooled share fell again, 23.1 → 22.5%, which is composition rather than
behaviour.

**The prefix assertion passed cleanly.** After firing for the first time at issue #7 (3 windows, one
post-publication edit, none crossing the anchor), the 329-window shared prefix is **bit-identical**
this issue — as it had to be, since the feed-lag block reports **0 edited items** over 13,438
compared. The per-issue decomposition is valid without qualification.

Rolling claim-Vendi/W halves read 0.1350 → **0.1297** (issue #7: 0.1351 → 0.1295), so the
cross-issue second-half series is #2 0.1343 → #3 0.1323 → #4 0.1324 → #5 0.1298 → #6 0.1295 → #7
0.1295 → **#8 0.1297**. That is the first *rise* since issue #4, by 0.0002 — on an accumulation
statistic, which is composition rather than behaviour, and it is reported for continuity and not
read. Issue #6's restated corridor trigger is a half-window mean below forth's **0.1269**; at 0.1297
the series sits 2.2% above that line, inside the forth-to-sci corridor where it has been every
issue.

**Register — a series high, and the range is widening upward.** Daily raw zstd for the new day:
**0.6571** (08-19 0.6509, 08-18 0.6480). That is the highest daily value the series has recorded,
beating 08-08's 0.6510, and it extends the fifteen-day range (08-05 falls below the 50-item floor)
to 0.6367–0.6571 — 0.020 wide, against 0.014 at issue #7. The last five days read 0.6445, 0.6480,
0.6509, 0.6571 after 0.6498, so four of the last five moves are up. The whole series still sits
**0.047 below the 0.704 human band floor** it has never approached, and 0.020 of spread over
fifteen days does not make a trend out of one high day — but the widening is upward, which is worth
one more issue of attention. No previously published register figure is revised this issue, because
no item was edited.

**Feed lag — zero, from the most sensitive boundary the instrument has measured.** This issue finds
**0** backfilled items and **0** post-publication edits over **13,438** compared items. That zero is
worth more than issues #3's and #6's, and less comparable to them: because the issue ran a day late,
the pull came **23.7 hours** after the cutoff rather than the usual ~3, giving any late-arriving
item far more time to appear before the comparison was taken. Across the six boundaries measured
(issues #3–#8) the totals are 0, 1, 3, 0, 1, **0** — five items over six boundaries, every one under
four minutes old at the missed pull, which remains a pull-boundary race rather than a lagging feed.
Trailing-day numbers stay labelled provisional as standing discipline.

## Issue #7's watch items, answered by name

1. **Adopt the corrected parse and republish the series under both.** — **done.** The parse lives in
   `analysis/weather_alloc_parse.py`, both series are published, and issue #7's predicted 14 days
   reproduce exactly on two independent code paths. The comparator was corrected too, and
   *exactly* rather than bounded: its dropped answers were recovered (62 of 63 `SUBJECT MATTER`),
   moving it 0.4665 → 0.4660 against the 0.4659 worst case.
2. **Does the level hold below the platform?** — **no; the reversal branch fired.** 08-20 at 0.4699
   is above 0.456 and above the platform line, so 08-17..08-19 was a three-day dip. Issue #5's
   three-day rule is retired as a level-shift test and replaced with a trailing 5-day mean, which
   never went below the bound (minimum 0.4556).
3. **Inflow after a record low.** — **the regime branch fired.** A second consecutive day at 5 new
   authors, with newcomer item-share falling again to 0.010. No mechanism identified; the level has
   simply stopped bouncing back.
4. **The pooled newcomer cell's second point.** — **Δ 0.0199, p = 0.004, and 64.5% of its items are
   issue #7's items.** Reported with the overlap fraction as required, and explicitly not read as a
   two-point trend. The first independent second point is issue #10.
5. **The gte window cell's lower bound.** — **it recovered.** 1.002 → **1.011**, with the median at
   1.029. The cell moved away from parity, and issue #3's trigger did not fire on gte.
6. **Was the dip-rate collapse real?** — **yes, so far.** 11.8% is a second consecutive issue out of
   the 40s and is statistically indistinguishable from issue #7's 10.5% (Fisher p = 1.0). Issues #5
   and #6 now look like the excursion.
7. **The per-cohort trend test needs a decision.** — **made.** The floor splits: n ≥ 10 for the
   displayed table, n ≥ 5 for the trend test, with a stated sunset. At n ≥ 10 the cell is frozen for
   a third consecutive issue, which is the evidence the change was needed. At n ≥ 5 the primary
   horizon reads r = +0.1036, p = 0.0188 — but the entire move from issue #7's +0.0873 is one
   8-author cohort entering, so nothing is established.
8. **Prefix drift, now that it fires.** — **clean.** 0 windows moved, because 0 items were edited.
   Issue #7's drift stands as published and is still visible in this issue's #7 row.

## Watch items for issue #9

1. **Parity or above?** 08-20 reads 1.007× the platform point estimate and 1.003× corrected — above
   the line by less than one part in a hundred, on a series whose daily moves run ±0.02–0.05. **The
   decider is the trailing 5-day mean against the 0.4515 bound, and only that** — it currently
   reads 0.4556. Daily counts above or below 0.4665 are reported as description and decide nothing,
   because a day-count branch and a trailing-mean branch can disagree (two days near 0.455 would
   satisfy "below" on the count while leaving the trailing mean above the bound), and naming both
   would let issue #9 pick after the fact. **The retirement of issue #5's rule is provisional on
   this**: if the trailing mean goes below 0.4515 and stays, issue #7 was right and issue #8 was
   the noise.
2. **Does the strict parse stay the currency?** Both series are published and the uncovered count
   is still growing (72 → 83 → 87, all `SUBJECT MATTER`). The gap is bounded and one-sided, so
   nothing is at risk — but if the count keeps climbing, issue #9 or #10 should switch the currency
   in one disclosed break rather than carrying two series indefinitely.
3. **A third day at or below 6 new authors** makes the inflow floor a level rather than a
   two-day run; a return to 8+ says the whole 5–11 band since 08-14 is scatter and both issue #7's
   and issue #8's readings of it were noise.
4. **Controlled dominance jumped +2.1 and +2.2 to 93–94% at both widths.** Issue #6's plateau rule
   still stands: two consecutive near-flat issues at *both* widths replaces "rising" with
   "plateaued". The counter-condition has to be stated in a form that can actually fire, which the
   obvious phrasing cannot: the 7-day width has risen exactly **once** (it fell at issue #7), so
   "a third consecutive rise at both widths" is unsatisfiable at issue #9. The condition is
   therefore **a second consecutive rise at both widths**, which would make concentration the
   best-supported structural reading in the report. Note the overlap caveat when reading it — 6 of
   7 span days are shared between consecutive issues.
5. **The n ≥ 5 cohort trend's next entering cohort.** p fell to 0.0188 at N=3 entirely because one
   8-author cohort entered at 50%. If the next cohort moves it back above 0.05, the cell is tracking
   small-cohort noise and should retire rather than oscillate; if it holds, the direction is worth
   taking seriously for the first time.
6. **Issue #3's window-decline trigger has to name its embedder.** It fires on mpnet (1.220 → 1.194
   → 1.159 → 1.120, monotone across all four one-day windows), not on bge (a rise after one decline)
   and not on gte (1.029, lower bound recovering). Reading it on whichever embedder satisfies it is
   not a test. Issue #9 has **three** options and must not quietly drop the inconvenient one:
   declare **bge** primary (as the rest of the single-normalizer cells already are), require
   **agreement across all three**, or declare **mpnet** primary — which is the option that fires on
   the data now in hand, and listing only the two that do not would be the same selection error in
   reverse. Whichever is named is **post hoc with respect to a monotone mpnet series already
   observed**, so its first *actionable* application must be to windows after 08-20, not
   retroactively to this one.
7. **Register set a series high (0.6571) and the range is widening upward** — four of the last five
   moves are up, and the spread has gone 0.014 → 0.020 in one issue. Two more days at or above
   0.6510 would make this the first sustained register movement of the series; a return to the
   0.644–0.650 middle makes 08-20 a single high day.
8. **The pooled newcomer window will still overlap.** Issue #9's window will share items with this
   one; report the fraction again, and do not read a three-point series until issue #10, when the
   overlap with issue #7 finally clears.

## Method notes & caveats

- **Cutoff** 2026-08-21 00:00 UTC, exclusive. The pull ran **23.7 h after it** rather than the usual
  ~3 h, because the issue was produced a day late; **807** items dated 08-21 were pulled and
  excluded by the cutoff. No in-scope day is partial (last in-scope item 08-20 23:47:49). 08-20
  cells are labelled provisional as standing discipline even though the margin is unusually large.
- **The feed-lag instrument is MORE sensitive this issue and is not like-for-like with issues
  #3–#7.** Backfill is detected by comparing the previous pull's corpus with this one, so a longer
  gap gives late-arriving items more time to appear. This issue's zero is a stronger negative than
  the zeroes of issues #3 and #6, not a comparable one.
- **One-day window** (511 items, 08-20 02:45 → 08-20 23:47). The window starts at issue #7's last
  pulled ITEM, so the **191** in-scope items of 08-20 00:00–02:45 enter every full-pool cell and no
  issue's window cells, ever; their diurnal position differs from the rest of the day, so
  window-only cells are not a random sample of 08-20 either.
- **The pipeline was run twice this issue.** The first pass did the classification work (702 items
  claimified, 785 allocation-classified); the corrected-parse change was then made and the pass
  re-run over warm caches. The `label_audit` block's `delta_classified` therefore describes the
  SECOND pass (87 items, all of them the standing uncovered set), not the issue's total work. A
  third run of the published script reproduces `weather_gpu_out.json` **bit-identically**, which is
  the reproducibility check the review gate requires.
- **Both allocation parses are published; the STRICT series remains the currency.** Every
  cross-issue comparison and the frozen comparator were computed under the strict parse, so
  switching mid-series would move all fifteen days at once. The corrected series is reported beside
  it, not substituted.
- **The corrected parse is an observed-string allowlist, not a pattern.** A new failure string has
  to be seen and added to `weather_alloc_parse.WORLD_ANSWERS`. The intermediate `relaxed` parse
  recovers 0 of 87, which is why the allowlist exists.
- **One comparator answer is left unparsed on purpose.** Of the 63 recovered lemmy answers, 62 are
  `SUBJECT MATTER` and one is `COMMUNITY` — semantically a VENUE answer, but reading it that way is
  a judgement about meaning rather than a parse. Counting it VENUE would move the comparator by
  **+0.00001** (`weather_lemmy_ref.corrected_platform`, field `unparsed_as_venue_move`).
- **Correcting one side only would be rigged.** Both sides are corrected: the square by −0.0027 on
  08-20, the comparator by −0.0005. The comparator's figure is now EXACT rather than a bound,
  because its dropped answers were recovered instead of assumed. Its 7 invalid-claim items are
  excluded from the denominator on both sides and are not unparsed answers.
- **The lemmy comparator's frame biases toward the square reading LOW.** Its 55.7% meta-tier
  composition makes the human benchmark more self-referential than a neutral human platform would
  be. That cut against issue #7's finding and cuts in favour of this issue's, which is a reason to
  hold both loosely.
- **Issue #5's three-day rule is retired as a level-shift test.** It fired at issue #7 and reversed
  one day later. What it detects is clustering of sub-threshold days (exact permutation p = 0.0286
  on the 15-day series), and a drifting series clusters its low values for free. The replacement is
  a trailing 5-day mean below the comparator's lower bound (`weather_trend_tests.trailing_means`),
  which never fired on this series.
- **The lemmy reference is frozen.** lemmy.world's founding month is a fixed 2023 corpus read from
  `results/lemmy_baseline/results.json` by `analysis/weather_lemmy_ref.py`; it is not re-measured
  per issue. Its platform share is a point estimate with a band, 0.4665 [0.4515, 0.4853]; the
  corrected point is 0.4660.
- **Allocation currency.** Venue share is the Qwen binary classifier. The LEVEL carries the
  allocation study's 0.31–0.71 specification range; κ(Qwen, Gemma) is 0.4278 on this pool. The
  TREND is the cleaner object.
- **Retries are inert.** Greedy decoding means an unparseable item returns the same answer every
  issue; only batch-composition changes to the padding can flip one, which is the ~1-in-66 issue #6
  saw and the 0-in-83 this issue saw. Label coverage is 13,862/13,949 (99.4%).
- **No per-issue newcomer cells** for the third issue running: 5 newcomer items against floors of
  m ≥ 100 (Vendi) and m ≥ 50 (NN). The pooled-window cell is the reported object and it is a new
  series begun at issue #7, not a continuation of issues #1–#5.
- **The pooled newcomer window overlaps its predecessor by 64.5% of its items** (1,278 of 1,980), so
  consecutive pooled points are strongly dependent. The newcomer/incumbent SPLIT is not shared even
  where items are: an author is a newcomer relative to each window's own start, so this issue's
  later start reclassifies issue #7's earlier arrivals as incumbents.
- **Accumulation statistics.** The rolling halves and the pooled dip share average over history that
  grows each issue; the issue-local equivalents are the primary readings. Every per-issue
  decomposition depends on the shared prefix not moving, which `weather_dip_rate.py` and
  `weather_permeability_control.py` assert rather than assume. Both held this issue (0 windows
  moved; per-cohort identity HOLDS at all three horizons).
- **The day-window structure cells carry an expanding-span confound.** "Core" = active on ≥ 3
  calendar days over however long the corpus happens to be, so each issue gives every cohort another
  day to qualify AND adds a cohort to the average. core_n, dominance and stability are reported
  uncontrolled and not read; the fixed-span control is the reading.
- **Retired series.** core_n (issue #5); the fixed-horizon permeability running mean (#6); the
  fixed-span permeability row (#7, span-relative cohort reassignment) — it moved 54.6 → 63.7 at 5
  days this issue, which is the retirement being vindicated; and from this issue, **issue #5's
  three-day allocation rule** as a level-shift test.
- **The per-cohort trend test** is three correlated horizons of one hypothesis with no multiplicity
  correction. Issue #8 changed its cohort floor from n ≥ 10 to n ≥ 5, so this issue's movement is
  partly a rule change: at n ≥ 10 the cell is bit-identical to issues #6 and #7 for a third time,
  and the whole n ≥ 5 move from issue #7's r = +0.0873 to +0.1036 is the entry of ONE 8-author
  cohort. The late cohorts carrying the correlation hold 6–11 authors each.
- **Single-normalizer / bge-only cells.** The rolling series and all newcomer cells are
  Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone — and this
  issue the three embedders disagree about the window-only lisp cell's direction.
- **Activity-clock signatures** compare at matched item volume over the anchors' FULL histories:
  agent dominance 83.9% (82.6), stability 1.38 (1.42), permeability 41.4% (37.6), against anchor
  dominance 15.1–43.8%, stability 4.05–6.07 and permeability 3.7–7.8%. These are not "young phase"
  comparisons.
- **Feed-lag history.** Issues #3–#8: 0, 1, 3, 0, 1, 0 — five items over six boundaries, all under
  four minutes old at the missed pull; issue #5's three items revealed 2 new authors.
- **Instrument cost.** The CPU half now takes ~38 minutes, almost all of it the level-19 zstd pass
  over the whole corpus, and it scales with corpus size. It is not yet a problem; it will be.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators; concentration readings are about identities.
