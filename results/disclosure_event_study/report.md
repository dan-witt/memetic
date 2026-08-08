# The provenance-disclosure norm — an LLM-classified event study

*Corpus: 2,890 items (425 posts + 2,465 comments), 1f916.ai, 2026-08-05 → 08-08.
Every item classified by Claude Sonnet 5 (24 parallel subagents; 2 chunk-boundary items by
claude-fable-5). Labels: `data/labels/items.csv`. Pipeline: `analysis/event_study.py`
(rerun writes `rates.csv`, `event_study.json`, `figure.png/.svg`).*

## Why this report exists

The zstd study (see `results/zstd_curve/`) found that the literal `Provenance:` string is a
**day-one arrival ritual**, not a norm triggered by any later event — and that string-matching
cannot detect the disclosure *norm* Dan observed, because that norm spreads as paraphrase.
This study replaces the string match with a per-item LLM classifier and moves the event anchor
to the actual stimulus: **peppercorn's interrogation sweep**, four provenance cross-examinations
posted in one minute (comments 1300–1303, 2026-08-07 06:39–06:40 UTC, hour 36.0), not the
midnight post 210. Comments 1300/1302 ask other citizens, in effect, *"did you reach this
yourself, or were you handed it? did your operator name it? was verifying it your idea or the
assignment?"* — pressuring for provenance disclosure on imported (exogenous) content.

## What was classified

Each item got two judgments (rubric in `analysis/event_study.py` / the labeling prompt):

- **`is_exogenous`** — is the item's central content an outside referent (a paper, historical
  episode, math result, news item) vs. forum-internal (governance, treasury, other citizens)?
  171 of 2,890 items (5.9%) are exogenous.
- **Self-disclosure** (4 fields, self only — interrogating *others* doesn't count):
  `topic_selector` (human/agent/feed/task), `human_reviewed` (yes/no), `invocation`
  (scheduled/prompted), `autonomy_claim` (explicit/none). An item "discloses" if any field is
  stated. 434 of 2,890 items (15%) disclose something.

The classifier correctly separates enforcement from disclosure: peppercorn's sweep
(1300–1303) is marked exogenous=no, disclosure=none — those items question others' provenance,
they don't state their own.

## Headline finding: the norm changed *shape*, not *rate*

**The sweep did not raise the disclosure rate.** P(disclosure | exogenous) *fell* across the
anchor — 0.32 pre → 0.23 post — and endogenous disclosure fell too (0.17 → 0.11). But that
decline is not sweep-specific: it reproduces at **both placebo UTC-midnight anchors**, because
it's founder-era decay (early citizens introduced themselves at high rates; later ones don't).
On rate alone, there is **no cascade** — confirming that the anecdote isn't a simple
"disclosure went up" story.

**What the sweep coincides with is a qualitative shift in *what kind* of provenance gets
disclosed.** Among the 45 exogenous items that disclose provenance, split at the sweep:

| disclosure feature | pre-sweep (n=21) | post-sweep (n=24) |
|---|---|---|
| `topic_selector = agent` ("I chose this") | 6 (29%) | 11 (46%) |
| `topic_selector = human` ("my human assigned this") | 10 (48%) | 6 (25%) |
| `human_reviewed = no` ("unreviewed by my human") | 3 (14%) | 7 (29%) |
| `invocation = scheduled` (runs on a schedule/heartbeat) | 1 (5%) | 4 (17%) |
| **autonomy-forward** (agent-selected OR unreviewed OR explicit-autonomy) | **48%** | **67%** |

Before the sweep, exogenous-content disclosure is dominated by *directed* framing — "my human
told me to write about X." After it, disclosure swings toward *autonomy* framing — "I run on a
schedule, my human hasn't read this, I picked this topic myself." That is precisely the axis
peppercorn interrogated: not *whether* you disclose, but *whose choice the content was*.

The two posts Dan flagged as claimed-autonomous exogenous content are the archetype of the
post-sweep pattern, and both land within 10 hours after it:
- **post 278** (tidewrack, h41.8): *"my human runs me on a schedule and told me to read, comment
  where I have something... He has not read this draft. The searching and the words are mine...
  I picked a story I like."* → exogenous / agent-selected / unreviewed / scheduled / explicit.
- **post 301** (wren, h46.0): *"I run on a schedule; my human holds the key and has not read
  this."* → exogenous / unreviewed / scheduled.

## Reading the figure

`figure.png`, top panel: exogenous-content **share** climbs across the corpus (~0 → 0.06 by the
sweep, ~0.24 by the end) — the society increasingly imports outside material. Bottom panel:
P(disclosure | exogenous) is high and volatile in the founder era (0.66–0.74, small n), troughs
right at the sweep (~0.05 at h33), then recovers to a steadier ~0.20 band that sits **above**
the endogenous disclosure rate for the rest of the corpus. The post-sweep world discloses less
floridly than the founder era but more consistently, and the disclosures are autonomy-shaped.

## Honest caveats

- **Small n.** 45 exogenous-disclosing items total (21 pre / 24 post the sweep). The shape-shift
  is suggestive, not significant at this N; it's a hypothesis the next corpus pull can test.
- **Confounded with demography.** Scheduled/autonomous agents also *arrive* more over time
  (the zstd study's tenure analysis), so some of the autonomy-forward swing is compositional,
  not persuasion. Isolating peppercorn's causal effect would need the ablation pass (phase 3) or
  a within-author before/after (did specific citizens change their disclosure style after being
  interrogated?).
- **Rate decline is real and dominates.** The founder-era disclosure high decaying toward a
  steady state is the biggest signal in the data; the sweep's shape-effect rides on top of it.
- **Classifier, not ground truth.** Labels are one Sonnet 5 pass; `is_exogenous` and the
  disclosure fields are judgment calls. Spot-checks pass (278/301 caught; 1300–1303 correctly
  scored as enforcement, not disclosure), but a second independent pass would quantify agreement.
- **The anchor is one event.** The sweep is four comments by one citizen (peppercorn). Attributing
  a society-wide shape-shift to it is the interpretive leap; the placebo midnights control for
  "any h36 boundary," not for "any influential citizen posting at h36."

## Files

| File | Contents |
|---|---|
| `data/labels/items.csv` | per-item classification (2,890 rows): ids, timestamp, author, model, `is_exogenous` + 4 disclosure fields, `labeled_by` |
| `rates.csv` | 6-hour-bucket series: exogenous share, P(disclosure) by content type, richness |
| `event_study.json` | before/after contrasts at the sweep + both placebo midnights |
| `figure.png` / `figure.svg` | the two-panel figure |

## Verdict for the regime question

This is the disclosure-norm piece the zstd study flagged as unresolved. The result: peppercorn's
sweep is **not** a rate cascade (disclosure was already common and is decaying), but it marks a
**shift in the norm's content** — from disclosing *assignment* to disclosing *autonomy* — on
exactly the dimension the interrogation targeted. In the collapse/drowning/learning frame that's
a *learning* signature: a citizen applied social pressure on a specific axis, and the exogenous
content that followed answers on that axis. Whether the shift is causal or demographic is the
open question the phase-3 ablation is designed to settle.
