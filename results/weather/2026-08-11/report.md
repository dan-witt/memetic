# 1f916 weather · 2026-08-11 (issue #1)

*A recurring health snapshot of the agent square, read against the frozen anchors of
[`results/novelty_bands`](../../novelty_bands/report.md). Corpus: fresh full pull, **708 posts +
5,214 comments = 5,922 items** (5,893 ≥ 20 chars), 440 authors, 2026-08-05 → 08-11 19:56 UTC
(6.05 days; final day partial). The corpus roughly doubled since the baseline pull (2,874 items).
Instrument set this issue: band placement, rolling idea series, register trend, churn signature,
cohort survival, inflows, newcomer-idea cell. New instruments may join later issues; each issue
states its set.*

![Three panels: the rolling idea-diversity series holding flat between the narrow-anchor band and the sci level; the author-inflow bar chart dominated by the Aug-6 spike, lower and non-monotone after; the raw-zstd register series flat and well below the human band floor.](figure.png)

## Readings

**Band placement — stable under extension.** agent/X (median subsample ratios, pull-2 vs
pull-1 in parentheses): lisp 1.273 (1.254) / 1.262 (1.266) / 1.078 (1.083) on bge/mpnet/gte; sci
0.675 (0.669) / 0.671 (0.669) / 0.768 (0.770); hn 0.631 (0.622) / 0.574 (0.567) / 0.729 (0.729).
Max drift ~0.02 — but note the pull-2 pool *contains* pull-1 (49% overlap), so this is stability
under extension, not independent replication. The clean delta-only corroboration is the rolling
series: its second half is built entirely from post-baseline windows and sits at 0.1352 vs the
baseline mean 0.1348. Five more days of discourse did not move the square's band position.
(Pull-1 reference cells mix two published post-processing variants; measured effect ≤ 0.005 —
see results.json.)

**Idea series — flat.** Rolling claim-Vendi/W holds at ~0.135 across all six days (halves 0.1349
/ 0.1352); no drift toward the lisp pole (narrowing) or the sci level (broadening). The series
runs between the forth level (0.127) and the sci level (0.162), dipping just below forth in ~10%
of windows at its low excursions; it never approaches the lisp/smalltalk/scheme cluster
(0.108–0.112).

**Register — flat, and still the outlier.** Daily raw-zstd novelty sits at 0.637–0.651 all week,
far below the human band floor (0.704). The house style is neither ossifying further nor
dissolving.

**Structure — a core-dominant venue with the door wide open.** First-ever agent churn signature
(agent-clock adaptation, author-attested in the pipeline before the pull: window = UTC day, core
= active ≥ 3 days): 131 core authors (30%) produce **76% of all items**, stability ratio 1.65,
newcomer→core permeability 30.5%. No number here is compared to the human anchors: their
signatures use year windows over decades, and a 3-of-6-days core is categorically easier to
enter than a 3-of-N-years one — day-window signatures of 6-day slices of the anchors' own young
histories would make this commensurable and are a candidate instrument for issue #2. The
qualitative shape is still informative: heavy core dominance with a core that most active
newcomers can still reach — an open door that mature human venues do not show at any window size
we've measured. Cohort survival, stated as measured: founding cohorts do **not** show a
persistence advantage — the Aug-5/6 cohorts have median 1–1.5 active days (Aug-6 next-day
survival 0.42) while the Aug-8/9 cohorts reach median 2.0 (next-day 0.45–0.46) despite shorter
horizons; ~22–42% of each cohort was still active on the final day; no cohort-ordering signal
yet. Author-arrival counts: 224 on Aug 6, then 64 / 46 / 56 / 33 / 11 — non-monotone, final day
partial (~13 pro-rated); the monotone decline signal is the **newcomer share of items**, 0.96 →
0.046 across the week.

**Newcomer idea diversity — parity, narrowly read.** Items by post-baseline newcomers vs
incumbents over the same period: within-pool claim-Vendi ratio 1.019 [0.995, 1.046] (bge;
item-subsampling band only). Newcomers are neither internally narrower nor wider than incumbents.
This cell measures each pool's *internal* spread — it cannot say whether newcomers bring *new*
claims or restate incumbent ones (identical Vendi is compatible with both); a cross-pool
instrument (union-vs-incumbent Vendi, or newcomer-claim distance to the incumbent claim cloud)
is the issue-#2 candidate for the refresh question.

## Watch items for next issue

1. **Permeability** — 30.5% is what young looks like; the watchable signal is its own
   issue-over-issue trajectory (a sustained fall = the door closing, the leaky-bucket transition
   beginning) — not its distance from the anchors' year-window figures, which are not
   commensurable.
2. **Inflow** — arrivals are well off the Aug-6 peak and newcomer item-share fell 0.96 → 0.046; whether
   arrivals stabilize or keep falling, one more issue decides.
3. **Idea corridor** — any sustained drift of the rolling series toward the narrow-anchor band.

## Method notes & caveats

Anchors and their claims are frozen from novelty_bands; only new agent items were claim-normalized
(delta pass, byte-identical Qwen pipeline, cache keyed by item id — post-baseline edits to old
items are not re-claimified). The time series and newcomer cell are single-normalizer (Qwen) and
bge-only; placement cells are 3-embedder but share the one-prompt monoculture. Day-window churn
is compared to the anchors' year-window signatures qualitatively only — no number crosses the
window boundary; the day/K=3 adaptation is author-attested (pipeline docstring), not registered.
Identity ≠ operator throughout
(uncorrectable without covenant-forbidden linking). Numbers in [`results.json`](results.json);
Figure panel A's x-axis is window index (nonuniform in clock time). Figure source [`analysis/weather_figure.py`](../../../analysis/weather_figure.py).
