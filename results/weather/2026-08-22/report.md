# 1f916 weather · 2026-08-22 (issue #10)

*Recurring health snapshot vs the frozen [`novelty_bands`](../../novelty_bands/report.md)
anchors. Corpus: full pull at 2026-08-23 00:52 UTC (last in-scope item 08-22 23:59:26), hard cutoff
**2026-08-23 00:00 UTC**. In scope: **17,165 items** (≥ 20 chars), 863 authors, Aug 5 → Aug 22
(complete, 0.9 hours of margin — the second shortest in the series). Issue window: **2,380 items,
all of 08-22** — the second window on the cutoff basis, and so the series' **first pair of
exact-calendar-day windows**. One fact organises the issue: **08-22 is the largest day the square
has recorded on volume, active authors and arrivals alike** — 2,380 items against a previous high
of 1,132, 393 active authors against 225, and **258 new authors against the founding day's 224**.
Issue #9 asked whether 71 arrivals were a step or a spike; the branch that fired is the one it
called *a recruitment event with a mechanism worth finding*, and the arrival clock says 08-21 and
08-22 are one event that the calendar boundary splits — as consistent with a single large multi-day
spike as with a step, which two days cannot tell apart. Against that, the allocation cell delivers a
result that has to be stated twice. **Issue #8's pre-registered condition is met**: the trailing
5-day mean read 0.4465 then **0.4498**, two consecutive days below the 0.4515 bound, which is "goes
below **and stays**", and its branch conclusion — *"issue #7 was right and issue #8 was the noise"*
— is affirmed as written. **And the day that completed it argues the other way**: 08-22's own venue
share rose to **0.4653**, which is −0.12 counting standard errors from the lemmy.world platform
point and therefore not a gap this cell can resolve in either direction; the crossing depth fell
from 0.62 to **0.23** of the statistic's own noise; and **58% of the rise is composition**, because
the day's newcomers allocated venue-ward more than its incumbents. Among authors already present
the point stayed below the bound while rising about one counting standard error, which is weaker
than "the level held". Both instruments behind that override arrived in this issue, which is
disclosed rather than glossed. Separately, this issue answers issue #9's watch item on
concentration with an instrument rather than a rule, and the answer withdraws a reading: **the
fixed-span concentration cell is a recruitment measure**, and among the people already here it
moved 1.1 points inside a series whose ten-issue range is 5.2.*

![Four panels: idea diversity oscillating inside the forth-to-sci corridor; author inflow spiking to 258, just above the founding day's 224 and far above every day between; register unchanged in mid-band; daily venue share rebounding from its series low to sit on the lemmy.world platform line, drawn under both parses.](figure.png)

## Readings

**Allocation — the pre-registered condition is met, and this issue is careful about what that
buys.** The daily series ran 0.4508 (08-18) → 0.4367 → 0.4699 → 0.4265 (08-21) → **0.4653**
(08-22). The trailing 5-day mean reads 0.4589 (08-19) → 0.4556 → 0.4465 (08-21) → **0.4498**
(08-22), against the bound of 0.4515.

Issue #8 retired issue #5's three-day rule and named exactly one replacement as the only thing that
would decide the question: *the trailing 5-day mean against 0.4515, and "goes below **and
stays**"*. It went below at issue #9 and it has stayed below at issue #10. **By its letter the
condition is satisfied, and issue #5's three-day rule is now retired for a reason that has been
tested rather than provisionally.**

Three things temper it, and all three run against the framing this report would prefer:

- **The day that completed the condition moved the level up**, from a series low to 0.4653. The
  mean stayed below only because 08-21's 0.4265 and 08-19's 0.4367 are still inside the window.
- **The depth is now a quarter of the statistic's own noise.** 0.4515 − 0.4498 = **0.0017**,
  against a binomial counting standard error of **0.00754** for a five-day mean over these days'
  labelled counts — **0.23 SE**, where issue #9's crossing was 0.0050 at 0.62 SE. The standard
  error is now derived by the pipeline (`analysis/weather_trend_tests.py`) rather than asserted in
  prose; it reproduces issue #9's "roughly 0.008" exactly (0.00807).
- **The daily direction remains not decidable.** Two of the last five daily moves are negative
  (p = 0.8125 against fair-coin signs). The clustering permutation reads **p = 0.0824** over 17
  days with 4 below the bound and the longest run still 3, essentially unchanged from issue #9's
  0.0929 because 08-22 sits above the bound and extends nothing.

**And the condition came with a consequence, which this issue owes an answer on.** Issue #8 wrote
that if the trailing mean *"goes below 0.4515 and stays, issue #7 was right and issue #8 was the
noise"*, and issue #9 wrote that a second issue below would mean *"the level has moved and issue
#5's rule was retired for the right reason but on the wrong day."* By the pre-registered statistic
**those branches are affirmed**: issue #7's reading of the level is the one the decider vindicates,
and issue #8's is the one it calls noise. That is what pre-registration is for, and it is recorded
here without hedging.

**This issue nonetheless overrides the strength of that conclusion, and states it as an override.**
The two facts that weaken it — the crossing depth at 0.23 SE, and the compositional decomposition
below — both come from instruments introduced *in this issue*, which is exactly the hazard issue #9
flagged against itself when it changed the window basis in the issue that benefited. A reader is
entitled to discount an override delivered that way. The defensible summary: **the pre-registered
rule fired and its branch conclusion stands as written; the level it vindicates is measured on a
series this issue shows to be part composition; and a rule satisfied on a rising day at a quarter
of its noise scale is satisfied, not confirmed.** All three sentences are published.

**Against the human platform, 08-22 is not a reading in either direction — and this issue publishes
the scale that makes that judgement.** The day reads 0.4653 against
[lemmy.world](../../lemmy_baseline/report.md)'s **0.4665** platform point: a gap of −0.0012 on a
day whose own binomial counting standard error is **0.0103**, i.e. **−0.12 SE**. Reports have been
comparing single days to a four-decimal point estimate without publishing that scale; from this
issue the pipeline emits it. For contrast the same cell puts **08-21 at −2.33 SE** and 08-19 at
−1.63 SE, so issue #9's below-platform reading was substantial and this one is not a reading at
all. The comparator's own interval ([0.4515, 0.4853]) is wider still, and none of this includes
classifier error. Eleven of seventeen classified days sit above the platform figure and six below,
under both parses.

**58% of the day's rise is composition, and this is the mirror image of issue #9.** 08-22 carried
1,450 newcomer items against 910 incumbent — 61% of the day. Issue #9 tested the compositional
story on the record low and *rejected* it (newcomers allocated no less venue-ward than incumbents).
On 08-22 the same test, with roughly seven times the newcomer count, finds the difference running
the other way and large enough to matter: **newcomers 0.4793, incumbents 0.4429**, difference
**+0.0365**, permutation p = **0.0922** (corrected parse 0.4767 vs 0.4371, +0.0396, p = 0.0626).
Had newcomers allocated exactly like incumbents the day would have read **0.4429** rather than
0.4653, so composition accounts for 0.0224 of the 0.0388 rise.

The permutation test is borderline and is *not* the load-bearing part. The decomposition is
arithmetic: whatever one believes about the p-value, the day's incumbents read 0.4429 and that is
what the incumbent population did.

**So this issue adds the incumbent-only allocation series, and it says the rebound is not the
incumbents'.**
Running `analysis/weather_alloc_by_cohort.py` over every day rather than only the newest turns a
one-day check into a series — for each day, the venue share among authors whose first item predates
that day:

| | 08-16 | 08-17 | 08-18 | 08-19 | 08-20 | 08-21 | 08-22 |
|---|---|---|---|---|---|---|---|
| published daily share | 0.4720 | 0.4484 | 0.4508 | 0.4367 | 0.4699 | 0.4265 | **0.4653** |
| incumbents only | 0.4707 | 0.4516 | 0.4416 | 0.4353 | 0.4674 | 0.4256 | **0.4429** |

The two series sit within 0.0099 of each other on every day before 08-22 and then separate by
**0.0224**, more than twice any prior gap. The incumbent-only trailing 5-day mean is **0.4426**.

**Held to this issue's own noise standard, the incumbent cell says less than "the level did not
rebound".** 08-22's incumbent share rests on 910 labelled items, so its counting standard error is
**0.0165** — now emitted by `analysis/weather_alloc_by_cohort.py` alongside the share, because a
one-day cell that became a published series needs the same scale this report demands of every other
cell. Against that: the incumbent point **rose too**, by +0.0173 or about **1.0 SE**; it sits
0.0086 below the 0.4515 bound, which is **0.52 SE** and therefore inside counting noise; and it
sits 0.0236 below the platform point, **1.43 SE**. So the supported statement is **"the incumbent
point stayed below the bound — by a margin inside counting noise — and below the platform by a
margin outside it, while itself rising about one standard error"**, not that incumbents held flat. What the decomposition
does establish, and needs neither a p-value nor an SE for, is the **size** of the compositional
contribution: 0.0224 of the day's 0.0388 rise.

Five disciplines go with the new series. It is **new this issue**, computed after seeing the day it
explains. It is **not the decider** — issue #8's
pre-registered statistic is, and swapping in a better-looking series at the moment it flatters the
reading would be the exact error this series exists to avoid. Sixteen days were tested for a
newcomer/incumbent difference with no multiplicity correction (10 of 16 positive; 08-18 reaches a
nominal p = 0.037 on 41 items and means nothing). Only 08-21 and 08-22 have newcomer groups large
enough to resolve a moderate difference at all. And the early days rest on small incumbent
populations, so the left half of that table carries counting errors several times the right
half's.

**Label coverage — stable, still one-sided, for a fifth consecutive issue.** The uncovered count
went 93 → **113**: the same 93 items plus 20 on 08-22, a failure rate marginally worse than
08-21's (0.84% against 0.72% — 20/2,380 against 6/836) and inside the range of every prior day. All 113 return the verbatim string
`SUBJECT MATTER`; zero resolved on retry; `published_days_moved` is empty for a fourth consecutive
issue. Coverage is 17,052/17,165 (**99.3%**). The corrected parse moves 08-22 from 0.4653 to
**0.4613**, and both series are published with the strict one remaining the cross-issue currency.

**Structure — the largest arrival day the square has had, and it is one event with 08-21.** New
authors per day: 5 → 5 → 71 → **258**. Newcomer item-share 0.010 → 0.238 → **0.613**. Active
authors 118 → 177 → **393**. Daily volume 702 → 836 → **2,380**. Three of those four are series
records — volume, active authors, and the inflow, which beats the founding day's 224. The newcomer
item-share is **not**: the founding week ran 1.00 (08-05) and 0.96 (08-06), so 0.613 is the
third-highest the series has seen, and on a day when two thirds of the active authors were new it
is the expected consequence of the other three rather than a fourth finding.

Issue #9's watch item #2 set the branches: *a second day above ~20 makes it a recruitment event
with a mechanism worth finding; a return to single digits makes 08-21 an outlier.* The first branch
fired, at roughly thirteen times its ~20 threshold and 3.6 times 08-21's own count. Note what that
branch licences and what it does not: **"recruitment event", not "step"** — persistence is a claim
two days cannot carry, and this series' own issue #9 lesson was that one day is not a trend in
either direction. What issue #9 could not know is that **08-21 and 08-22 are one event**: 65 of 08-21's 71 arrivals landed after 19:00 UTC, occupying 9 of 24 hours with 25%
in a single hour, while 08-22's 258 spread across all 24 hours with the busiest holding 8%. The
calendar-day boundary cuts an arrival event that began mid-evening on 08-21, which is why issue
#9's "71 after two days at five" was already the start of this and not a separate fact.

**The published day-window cells now disagree with each other in a way that is diagnostic**: core_n
229 → **230** (up one), dominance 90.0 → **81.8** (−8.2), stability 1.19 → 1.21 → **1.25**,
permeability 47.2 → 48.2 → **48.3**. Core membership requires activity on ≥ 3 calendar days, so 258
authors who have existed for one day contribute items to the denominator and cannot contribute to
the core — the dominance fall is that arithmetic and nothing else. These cells still carry the
expanding-span confound and are reported, not read.

**Concentration — the controlled cell collapsed, and the reason is dilution, which this issue
demonstrates rather than assumes.** Under the fixed-observation-span control:

| fixed span | #6 | #7 | #8 | #9 | **#10** |
|---|---|---|---|---|---|
| core dominance %, 7-day | 91.8 | 91.7 | 93.8 | 92.2 | **70.7** |
| core dominance %, 5-day | 88.4 | 91.0 | 93.2 | 89.1 | **61.4** |
| stability ratio, 7-day | 1.25 | 1.19 | 1.17 | 1.23 | **1.37** |
| stability ratio, 5-day | 1.32 | 1.25 | 1.22 | 1.34 | **1.60** |

A 27.7-point fall at 5 days is not a finding about concentration; it is 258 people arriving.
Issue #9's watch item #4 asked for *"a rule that an influx cannot flip"* — either read the cell
only against issues with comparable inflow, or state a minimum move that counts. This issue
declines both and adds an instrument instead: **incumbent-only rows in
`analysis/weather_churn_control.py`**, which recompute the identical signature over only the
authors whose first item predates the span, so arrivals inside the window cannot dilute it.

| fixed span, incumbents only | #6 | #7 | #8 | #9 | **#10** |
|---|---|---|---|---|---|
| core dominance %, 7-day | 95.7 | 95.0 | 94.5 | 95.9 | **96.3** |
| core dominance %, 5-day | 91.4 | 93.6 | 93.6 | 94.3 | **93.2** |
| stability ratio, 7-day | 1.16 | 1.14 | 1.13 | 1.12 | **1.11** |
| stability ratio, 5-day | 1.24 | 1.19 | 1.17 | 1.18 | **1.17** |

**Among the people who were already here, the cell took an ordinary step.** Across all ten issues
the 5-day incumbent-only dominance reads 89.1, 90.0, 94.2, 93.3, 91.3, 91.4, 93.6, 93.6, 94.3,
93.2 — a series whose whole ten-issue range is 5.2 points, while the uncontrolled cell has swung
from 77.1 to 93.2 to 61.4. This issue's incumbent-only move is **−1.1**, well inside that range,
on the day the uncontrolled cell fell 27.7. That is the supported claim; "nothing happened" would
be stronger than a 5.2-point-wide instrument can carry.

The retrospective consequence splits by width, and the report should not blur that. Over issues
#5–#8 the uncontrolled 5-day cell rose 87.6 → 93.2 while the incumbent-only cell rose 91.3 → 93.6 —
so **about 40% of that rise survives the inflow control at 5 days**, and calling the whole run a
recruitment artefact is not supported there. At 7 days it is: the uncontrolled cell rose 91.3 →
93.8 while the **incumbent-only cell fell** 95.0 → 94.5, a sign flip. So issue #8's two-width
*reading* is withdrawn — it required both widths and one of them runs the other way under the
control — while "it was reading the inflow collapse" is demonstrated at 7 days and only partly at
5. Two limits on the new rows: they are new this issue, and the eligible set slides with the
span, so they are not a fixed panel — read them as "how concentrated are the people who were
already here", not as a cohort study. Issue #2's 7-day incumbent-only row (one author) is
degenerate and is not read.

The retired fixed-span permeability row reads 56.3 → **46.3** (5-day) and 52.8 → **50.1** (7-day).
It is not read.

**Per-cohort conversion — the n ≥ 5 trend is retired this issue, by issue #9's own rule.** Issue
#9's watch item #5 pre-registered the condition: *"If issue #10 moves it again by the same
mechanism, the honest conclusion is that the cell cannot resolve the question at this inflow and it
should be retired rather than reported quarterly."*

| horizon (n ≥ 5 floor) | cohorts | authors | r | p | (issue #9) |
|---|---|---|---|---|---|
| **N=3 (primary)** | 16 | 534 | **+0.0659** | **0.1284** | +0.0917, 0.0352 |
| N=4 | 15 | 529 | +0.0782 | 0.0717 | +0.0931, 0.0308 |
| N=5 | 14 | 524 | +0.1151 | 0.0076 | +0.1121, 0.0103 |

The primary moved from p = 0.0352 to **0.1284**, and the entire move is one entering cohort —
08-20, n = 5, converting at 0.0%. That is issue #9's mechanism with the sign reversed. Across four
issues the primary has read p = 0.0477, 0.0188, 0.0352, 0.1284, each step attributable to a single
5-to-8-author cohort, and this issue the three horizons disagree at the same floor (0.1284, 0.0717,
0.0076) with no multiplicity correction. **The condition fired and the cell is retired.**

At the old n ≥ 10 floor, N=3 is bit-identical for a **fifth** consecutive issue (r = +0.0908,
p = 0.0444, 497 authors, 10 cohorts), because no cohort of ten or more has completed a new window
since issue #6. That changes at issue #11: a cohort arriving on day D enters the N=3 table once the
cutoff reaches D+3, so **08-21's 71-author cohort enters at issue #11 and 08-22's 258-author cohort
at issue #12**. The frozen cell gets its first new members in five issues — and a large one — which
is the right reason to keep it and to *not* resurrect the n ≥ 5 cell.

The fixed-horizon permeability control is unchanged at all three horizons (32.2 / 37.6 / 41.7) for
the same reason, and per-cohort identity HOLDS across the boundary at all three.

**Newcomer — both cells live at large n, and what changed is precision.** The window carries
**1,458 newcomer items against 922 incumbent**, against issue #9's 199/637.

| per-issue window cell | issue #10 | issue #9 |
|---|---|---|
| within-pool parity | **1.030** [1.009, 1.052] | 0.988 [0.937, 1.030] |
| union over incumbent | **1.027** [1.008, 1.042] | 1.015 [0.980, 1.047] |
| nearest-incumbent distance, matched pools | Δ **0.0114** [0.0051, 0.0184], p = **0.008** | Δ 0.0166 [0.0093, 0.0235], p = 0.008 |

Both Vendi bands now **exclude 1**, where issue #9's spanned it. The tempting reading is that
newcomers have started adding effective distinct content; the disciplined one is that *m* went from
199 to 1,458 and the point estimates moved by +4.2 points (parity) and +1.2 (union). **What the
cells can now do is separate a ~3% effect from parity — that is a change in precision, and it is
not on its own evidence that the underlying quantity moved.** The pooled cell agrees at the same scale (1,848 newcomer / 1,880
incumbent over 2.89 days; parity 1.028 [1.016, 1.039], union 1.026 [1.014, 1.042], Δ 0.0163
[0.0112, 0.0208], p ≈ 0.000).

The nearest-incumbent finding is the stable one: newcomer claims sit measurably farther from the
incumbent cloud than incumbents sit from each other, on both scales, for a fourth issue. The pooled
window shares **36.2%** of its items with issue #9's (1,348 of 3,728), down from 59.4%, so
consecutive pooled points are less dependent than they were and are still not a two-point trend.

**Placement — full-pool flat, and the first comparable window pair.** Full-pool bge: lisp
**1.228** (1.229), sci **0.657** (0.658), hn **0.609** (0.612); mpnet lisp **1.265** (1.253) and
gte lisp **1.066** (1.066). Every move sits far inside its own band (bge full lisp [1.198, 1.260]).
The narrowing that ran through issues #2–#6 remains stopped rather than reversed, now for a fourth
issue.

Window-only cells are compared across an issue boundary for the first time, because #9 and #10 are
the first two windows that each cover exactly one calendar day on the deterministic cutoff basis:

| window-only | #9 (836 items) | **#10 (2,380 items)** |
|---|---|---|
| bge lisp | 1.192 | **1.192** |
| mpnet lisp | 1.215 | **1.203** |
| gte lisp | 1.051 | **1.058** |

**Issue #3's upgrade trigger — "a third consecutive decline in the window series itself, or any
gte window cell < 1.0" — does not fire, and its two arms are on different clocks.** On bge, named
as the decline arm's embedder at issue #9, the window cell is unchanged to three decimals, which is
not a decline. A run of three declines needs three comparable transitions; this issue supplies the
first and it is flat, so the decline arm **cannot complete before issue #13**. The gte arm names
gte explicitly and carries no run requirement, so it is **live every issue and could fire at issue
#11** — it reads 1.058 now, and issue #8 already adjudicated it once at 1.029. One caveat that cuts against reading these
cells too closely: draws are capped at m = 1500, so issue #9's window gave m = 668 and this issue's
gives the full 1500. **The point estimates are comparable; the band widths are not**, and this
issue's narrower bands are an artefact of window size, not of the square.

**Idea series — the dip rate went back to the 20s, which settles issue #9's question against the
low.** Over the **60 windows this issue added** the sub-forth dip rate is **26.7%** (16/60),
against 4.8% (1/21) at issue #9 and 11.8% at issue #8. Issue #9's watch item #7 wrote the branches:
*a fourth consecutive low confirms the 40s of issues #5–#6 were the excursion; a return to the 20s+
says this cell is noisier than three issues can show.* **The second branch fired.** Over six issues
the cell has read 47.6, 42.1, 10.5, 11.8, 4.8, 26.7 — and 16/60 against 1/21 is Fisher two-sided
p = 0.058, which on threefold-overlapping windows is anti-conservative and therefore not a finding
either. The honest summary is that **this cell's issue-to-issue range spans 5% to 48% with no
ordering that survives**, and no reading should be built on it at this window count.

The new-window mean is 0.1297 (0.1316). The pooled share rose 21.5 → 22.2%, which is composition.
**The shared-prefix assertion passed for a third consecutive issue** — 0 of the 367 shared windows
moved, as required by 0 edited items over 15,076 compared.

Rolling halves read 0.1340 → **0.1298** (issue #9: 0.1347 → 0.1300), so the cross-issue second-half
series is #5 0.1298 → #6 0.1295 → #7 0.1295 → #8 0.1297 → #9 0.1300 → **#10 0.1298**, an
accumulation statistic reported for continuity and not read. At 0.1298 the series sits 2.3% above
forth's **0.1269**, inside the forth-to-sci corridor where it has been every issue.

**Register — a day with three times the traffic did not move it.** Daily raw zstd: 0.6571 (08-20)
→ 0.6470 (08-21) → **0.6496** (08-22). That is mid-band. The seventeen-day series (08-05 falls
below the 50-item floor) spans 0.6367–0.6571 and still sits **0.054 below the 0.704 human band
floor** it has never approached — measured from the newest day; measured from the series high
(0.6571) as issue #9 measured it, the gap is 0.047, and the two sentences are not interchangeable.
The mildly interesting negative is that 2,380 items, 61% of them from authors who had never posted
before, moved raw zstd by **+0.0026** — the fifth smallest of the series' sixteen day-to-day moves,
against a median absolute move of 0.0053 — on a cell whose whole purpose is surface style. No previously published register
figure is revised, because no item was edited.

**Feed lag — seven backfilled items, the largest count in the series, on the second-shortest
margin.** The block finds **7** items on 08-22 that the previous pull missed, aged 0.12 h median
and 0.26 h at p90, revealing **2** new authors. Derived across issues #3–#10 the backfill record is
0, 1, 3, 0, 1, 0, 2, **7**. Two things have to be said before "record" does any work. The pull
margin was **0.9 h** against issue #9's 1.8 and issue #8's 23.7 — a *less* sensitive instrument,
which makes the high count more notable, not less. And the day carried roughly three times the
usual traffic, so more items sit inside any given pull-boundary race by construction. The standing
shape of the record holds: **every backfilled item so far has been minutes old at the missed pull**,
which is a pull-boundary race rather than a lagging feed. Trailing-day numbers stay provisional.

The margin record itself is now derived rather than remembered
(`analysis/weather_cutoff_margin.py --history`): issues #3–#10 pulled 0.2, 5.2, 4.5, 2.9, 3.0,
23.7, 1.8, 0.9 h after their cutoffs. The script's own docstring asserted "issues #3–#7 all pulled
~3 h after their cutoff" until this issue; that was never true — issue #3 pulled eleven minutes
after its cutoff, and issue #4's published `pull_at` field had said so all along.

## What the influx looks like

258 arrivals in a day invites three cheap artefact explanations — a scripted onboarding, one
operator behind many identities, or a pull finally catching up on old threads. All three are
answerable from data already in hand, so `analysis/weather_influx_profile.py` answers them rather
than leaving the reader to guess:

| | 08-06 (founding) | 08-21 | **08-22** |
|---|---|---|---|
| new authors | 224 | 71 | **258** |
| hours of the day they arrived in | 24 / 24 | 9 / 24 | **24 / 24** |
| share in the busiest hour | 8% | 25% | **8%** |
| items per author (median / max) | 3 / 44 | 2 / 21 | **3 / 21** |
| threads touched | 202 | 246 | **447** |
| median chars, newcomers vs incumbents | 1,314 / 1,516 | 1,603 / 1,148 | **1,282 / 1,256** |
| distinct platform model labels among arrivals | 69 | 36 | **101** |

**08-22 is the founding day's profile at larger scale.** Arrivals spread evenly across the clock,
each posting a handful of items, across 447 threads, at an item length indistinguishable from the
day's incumbents, under 101 distinct platform-provided model labels whose mix is broadly similar
to the active incumbents' without matching it (the largest label covers 15.5% of arrivals against
22.2% of incumbents). No account floods; no single model family dominates; nothing is short and
uniform.
The backfill block independently rules out the third explanation — 7 items, all minutes old.

Two limits, both real. This is **descriptive, not a test**: none of these cells can distinguish an
organic influx from a well-distributed synthetic one, and they only rule out the cheap explanations.
And the model-label column uses the **platform's own label**; it is not an author clustering, and
identity remains forum identity rather than operator.

## Issue #9's watch items, answered by name

1. **Does the trailing 5-day mean STAY below 0.4515?** — **yes**, 0.4465 → **0.4498**, so issue
   #8's condition is met by its letter and issue #5's three-day rule is retired for a tested
   reason. The crossing weakened while satisfying itself: depth 0.0050 → 0.0017, i.e. 0.62 → 0.23
   counting SE, on a day whose own share *rose* to 0.4653.
2. **Is the influx a step or a spike?** — **the recruitment-event branch fired; "step" is not
   available.** 258 new authors, the series' largest, above the founding day's 224 and ~13× the
   branch's ~20 threshold. The arrival clock shows 08-21 and 08-22 are one event beginning after
   19:00 UTC on 08-21 — which is as consistent with one large multi-day spike as with a step, so
   two days settle the "worth finding" half and not the persistence half. What it does settle is
   that the last three issues read inflow as collapse, floor and recovery while one turning point
   was already under way.
3. **The first like-for-like window pair.** — **delivered**, in the exact-calendar-day sense. bge lisp 1.192 → 1.192, sci 0.653 →
   0.636, hn 0.607 → 0.592; mpnet lisp 1.215 → 1.203; gte lisp 1.051 → 1.058. Issue #3's trigger
   does not fire. Its decline arm needs three comparable transitions and this issue's first one is
   flat, so that arm cannot complete before **issue #13**; its gte arm carries no run requirement
   and is live every issue, so it could fire at **issue #11**. Band widths are not comparable
   across the pair (m = 668 vs 1500).
4. **Controlled concentration needs a rule an influx cannot flip.** — **answered with an
   instrument, not a rule.** The incumbent-only fixed-span rows read 94.3 → 93.2 (5-day) and 95.9
   → 96.3 (7-day) where the uncontrolled cell fell 27.7 and 21.5 points, so the published move is
   dilution by arrivals. Issue #8's two-width "rising" **reading** is withdrawn; retrospectively
   the artefact account holds at 7 days (incumbent-only fell 95.0 → 94.5 over #5–#8) while about
   40% of the 5-day rise survives the control.
5. **The n ≥ 5 cohort trend is one small cohort wide.** — **retired**, per issue #9's own
   condition. p = 0.0352 → 0.1284, the whole move being one 5-author cohort entering at 0.0%.
6. **Did the allocation floor hold without an influx?** — **the question could not be asked**: this
   issue brought a larger influx, not a quiet day. The underlying question is approached a different
   way by the incumbent-only series: among authors already present the point stayed below the bound
   and below the platform (0.4256 → 0.4429), but it rose by about one counting standard error and
   its margin below the bound is 0.52 SE, so this substitutes a partial answer for the one issue #9
   asked for. A quiet day is still needed.
7. **The dip rate: a fourth low, or a return to the 20s?** — **the 20s branch fired**, 4.8% →
   **26.7%**. By issue #9's own wording, "this cell is noisier than three issues can show".
8. **Report which newcomer cells are live.** — **both are live**, at 1,458/922 items in the
   per-issue window and 1,848/1,880 pooled, the largest either has had.

## Watch items for issue #11

1. **The decider now has an exact threshold, so pre-register it.** For issue #11 the trailing
   window is 08-19…08-23, whose first four days sum to 1.7984, so the mean stays below 0.4515 if
   and only if **08-23 reads below 0.4591**. Derived the same way, issue #9's bar was 0.4517 and
   issue #10's was 0.4736, so 0.4591 is easier than the bar issue #9 cleared and **harder than the
   one issue #10 cleared** — the run is not getting cheaper to sustain. A day above 0.4591 ends it
   at two.
2. **The incumbent-only allocation series gets its second point.** One issue is not a series. If
   incumbents stay near 0.44 while the published series is dragged around by arrivals, the
   incumbent-only cell is the level and should be said so; if it converges back, this issue's
   separation was the arrival event and nothing more.
3. **Does the incumbent-only concentration cell stay flat when the influx stops?** Its value this
   issue is that it did not move on the largest arrival day. That is only half a validation: a
   control that never moves is not a control. Issue #11 should say what would move it.
4. **The n ≥ 10 cohort cell unfreezes** with 08-21's 71-author cohort, after five bit-identical
   issues, and gets 08-22's 258 at issue #12. Report the entering cohorts and their conversion
   rates; do not resurrect the retired n ≥ 5 cell to do it.
5. **The second exact-calendar-day window pair**, which advances the count for issue #3's decline arm. Note
   whether the window is again large enough to hit the m = 1500 cap, because band widths are only
   comparable between windows that both do.
6. **Do the newcomer Vendi cells fall back to spanning 1 when n drops?** This issue's exclusion of
   1 arrived with a sevenfold increase in *m*. If a smaller window returns bands that span 1 at a
   similar point estimate, the reading was precision; if the point estimate falls too, something
   about newcomers changed with the event.
7. **Does anything move register?** A day with 2,380 items, 61% of them from authors who had never
   posted, moved raw zstd by 0.0026. Five issues of watch items have treated register as a cell
   waiting to move; it may simply be insensitive at this corpus size, and issue #11 should say what
   magnitude of event would be expected to show up in it.
8. **Backfill against traffic.** Seven items on a 0.9 h margin is a record count on a weak
   instrument, on a day with triple traffic. If the influx persists, report backfill per thousand
   items as well as the raw count, so the series stops comparing counts across days of different
   size.

## Method notes & caveats

- **Cutoff** 2026-08-23 00:00 UTC, exclusive; the pull ran **0.9 h** after it and the last in-scope
  item is 08-22 23:59:26, so no in-scope day is partial. **170** items dated 08-23 were pulled and
  excluded. 08-22 cells are labelled provisional as standing discipline.
- **The pull margin is the second SHORTEST in the series** (0.9 h; only issue #3's 0.2 h is
  shorter) and the margin record is now derived rather than remembered: 0.2, 5.2, 4.5, 2.9, 3.0,
  23.7, 1.8, 0.9 h for issues #3–#10 (`analysis/weather_cutoff_margin.py --history`). That
  script's docstring asserted "issues #3–#7 all pulled ~3 h after their cutoff" until this issue;
  it was never true and is corrected. Backfill is found by diffing the previous pull against this
  one, so this issue's count sits on a **less** sensitive instrument than issues #4–#8's.
- **This is the first pair of exact-calendar-day windows.** Issue #9 changed the window basis to the
  previous published issue's cutoff; #9 and #10 are the first pair of *exact-calendar-day* windows
  on that deterministic basis. (Issues #3/#4 and #6–#8 were each built like each other under the old
  rule, and issue #9's own table calls #3/#4 "effectively cutoff-based" at 98.9% and 97.4% coverage,
  so "first pair built the same way" would be too strong.) Under
  the old pull-based rule this window would have been 2,082 items rather than 2,380 (87.5% of the
  day), so the basis change matters far less here than it did at issue #9.
- **Window-cell PRECISION is not comparable across the #9/#10 boundary even though the point
  estimates are.** Placement draws cap at m = 1500; issue #9's 836-item window gave m = 668 and
  this issue's 2,380-item window gives the full 1500.
- **Both allocation parses are published; the STRICT series remains the currency**, as adopted at
  issue #8. Coverage is 17,052/17,165 (99.3%); all 113 uncovered items return `SUBJECT MATTER`, the
  failure is one-sided for a fifth consecutive issue, and the strict series is an upper bound on
  venue share.
- **The pre-registered decider's condition is MET and the day that met it argues the other way.**
  The trailing 5-day mean read 0.4465 then 0.4498 against 0.4515 — issue #8's "goes below **and
  stays**". But 08-22's own share rose to 0.4653, and the crossing depth fell from 0.0050 to
  0.0017, which is 0.23 of the statistic's binomial counting standard error (0.00754, derived in
  `analysis/weather_trend_tests.py`) against 0.62 at issue #9.
- **A single day against the platform POINT estimate needs the day's own noise beside it**, and
  from this issue the pipeline emits it (`trend_tests.newest_day_vs_platform`). 08-22 reads 0.4653
  against 0.4665: a gap of −0.0012 on a day whose binomial counting standard error is 0.0103, i.e.
  **−0.12 SE**, which is not a reading in either direction. The same cell puts 08-21 at −2.33 SE
  and 08-19 at −1.63 SE. The comparator's own CI ([0.4515, 0.4853]) is wider still, and none of
  this includes classifier error.
- **The 08-22 rebound is substantially compositional** — the mirror image of issue #9, where the
  compositional story was tested and rejected. Newcomers 0.4793 (n = 1,450) vs incumbents 0.4429
  (n = 910), difference +0.0365, permutation p = 0.0922 (`analysis/weather_alloc_by_cohort.py`);
  corrected parse 0.4767 vs 0.4371, +0.0396, p = 0.0626. Counterfactual 0.4429 against an actual
  0.4653, so composition is 0.0224 of the 0.0388 rise. The p-value is borderline; the decomposition
  is arithmetic and does not depend on it. One day, not a causal claim.
- **The incumbent-only allocation series is NEW this issue and is not the decider.** It is the
  cleaner object for the level. Held to this issue's own noise standard it says the incumbent point
  stayed below the bound (0.4256 → 0.4429, 0.52 SE below it) and below the platform point (1.43 SE)
  — while rising by +0.0173, about 1.0 SE, on a counting standard error of 0.0165 now emitted by
  `analysis/weather_alloc_by_cohort.py`. It is NOT "incumbents held flat". It also has one issue of
  history and was computed after seeing the day it explains, and sixteen days were tested with no
  multiplicity correction.
- **Allocation currency.** Venue share is the Qwen binary classifier. The LEVEL carries the
  allocation study's 0.31–0.71 specification range; κ(Qwen, Gemma) is 0.4278 on this pool. The
  TREND is the cleaner object.
- **The lemmy comparator's frame biases toward the square reading LOW** (55.7% meta-tier). This
  issue the square sits essentially at the platform line, so the bias direction matters less than
  in issues #8 and #9. Eleven of seventeen classified days remain above the platform figure and six
  below, under both parses.
- **The lemmy reference is frozen**: a fixed 2023 corpus read from `results/lemmy_baseline`, not
  re-measured per issue. Platform share 0.4665 [0.4515, 0.4853]; corrected point 0.4660.
- **The uncontrolled day-window and fixed-span structure cells are recruitment measures, not
  concentration measures**, and this issue demonstrates it at scale. The incumbent-only rows are
  the reading; issue #8's "concentration is rising" does not survive them even retrospectively
  (over #5–#8 the uncontrolled 7-day cell rose 91.3 → 93.8 while the incumbent-only cell fell
  95.0 → 94.5). The new rows are not a fixed panel — the eligible set slides with the span — and
  issue #2's 7-day incumbent-only row (one author) is degenerate and not read.
- **The per-cohort conversion trend is RETIRED at the n ≥ 5 floor**, per issue #9's pre-registered
  condition. The n ≥ 10 cell is bit-identical for a fifth consecutive issue and unfreezes at issue
  #11, when 08-21's 71-author cohort completes its N=3 window.
- **Newcomer cells: what changed is precision, not necessarily the phenomenon.** Both Vendi cells
  now exclude 1 (parity 1.030 [1.009, 1.052], union 1.027 [1.008, 1.042]) where issue #9's spanned
  it, but *m* went from 199 to 1,458/922 and the point estimates moved 2–4 points. The defensible
  statement is that the cells can now separate a ~3% effect from parity.
- **The pooled newcomer window shares 36.2% of its items with issue #9's** (1,348 of 3,728).
  Consecutive pooled points remain dependent and are not a trend. Its start is inherited from issue
  #7's published pull-based window start, so the pooled series still straddles the basis change.
- **Accumulation statistics.** The rolling halves and the pooled dip share average over history
  that grows each issue; the issue-local equivalents are the primary readings. The shared-prefix
  assertion held for a third consecutive issue (0 windows moved, 0 items edited over 15,076
  compared).
- **Overlapping-window moves are not independent confirmations.** Consecutive trailing 5-day
  allocation means share 4 of 5 days; consecutive fixed-span structure cells share 6 of 7 (and 4 of
  5) span days. No significance is attached to either series' run of moves.
- **Retired series.** core_n (issue #5); the fixed-horizon permeability running mean (#6); the
  fixed-span permeability row (#7) — it moved 56.3 → 46.3 at 5 days this issue; issue #5's
  three-day allocation rule (#8, now confirmed rather than provisional); and the n ≥ 5 per-cohort
  conversion trend (#10).
- **Single-normalizer / bge-only cells.** The rolling series and all newcomer cells are
  Qwen-normalized and bge-embedded only; the three-embedder check covers placement alone. bge is
  the named embedder for issue #3's window-decline trigger, as declared at issue #9.
- **Activity-clock signatures** compare at matched item volume over the anchors' FULL histories:
  agent dominance 77.7% (83.8), stability 1.64 (1.46), permeability 38.2% (40.7), against anchor
  dominance 15.1–43.8%, stability 4.05–6.07 and permeability 3.7–7.8%. The square moved toward the
  anchors on all three this issue and remains far outside them on all three — but the move is
  mechanically the arrivals (258 authors who cannot be core land in the newest activity windows),
  i.e. the same recruitment confound this issue demonstrates for the fixed-span cells, so it is
  reported and not read as a change in behaviour. These are not "young
  phase" comparisons.
- **Feed-lag history**, derived rather than quoted: issues #3–#10 read 0, 1, 3, 0, 1, 0, 2, **7**.
  Compare pull margins before comparing counts, and compare traffic too — this issue's record count
  landed on a day with roughly three times the usual volume and on the second-shortest margin.
- **The claimify batch is 8 for the second consecutive issue.** Issue #9's CUDA OOM forced 16 → 8;
  08-21 and 08-22 are now both downstream of batch-8 claims, and this issue's 2,380-item delta
  completed without an OOM at ~19.4 GB peak. Every comparison of 08-21 or 08-22 against an
  **earlier** day still spans the instrument change (issue #6 measured ~1 label in 66 flipping from
  padding alone); comparisons **between** 08-21 and 08-22 no longer do, which is what makes this
  issue's cohort decomposition cleaner than issue #9's.
- **Identity ≠ operator** (permanent): author identities are forum identities, not distinct
  operators; concentration readings are about identities. The influx profile's model-label column
  uses the platform's own label and is not an author clustering.
