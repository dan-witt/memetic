# Ritual accumulation as compressibility — zstd curve over the 1f916.ai corpus

*Corpus: 425 posts + 2,465 comments (5.2M chars), 2026-08-05 18:41 UTC → 2026-08-08 20:14 UTC (73.5 h).
Pipeline: `analysis/zstd_curve.py` (rerun with `analysis/run.sh`). Run parameters and sanity checks: `run.json`.*

## Headline findings

1. **Ritual mass is large: about a third of the corpus's description length is shared material.**
   Standalone, items cost 4.16 bits/char; conditioned on the trailing 512 KB of forum history,
   2.68 bits/char — history conditioning removes **35.6%** of the bits (39.5% with full history).
2. **But ritualization is not (yet) increasing.** The hypothesis was that accumulating rituals
   drag per-token information down over time. The compression instrument says the opposite,
   weakly: the novelty ratio *rises* over the steady-state span — 0.631 → 0.638 → 0.650 by
   thirds, a per-item trend of **+0.0065/day**. Per-token information is stable to slightly
   increasing over the forum's first three days. The most self-similar phase was the *early*
   forum (hours 10–25, novelty ≈ 0.61–0.63), before the population diversified (338 distinct
   authors on 8+ model families by the end).
3. **Recency carries real signal.** The window-conditioned ratio sits a stable ~1.6 percentage
   points *below* the shuffled-history control throughout — the immediately-preceding 512 KB
   predicts new items better than a same-sized random sample of the corpus. Local conversational
   structure (reply quoting, live memes) is measurable and roughly constant. The shuffled control
   also rises in the last third (0.648 → 0.666), meaning late items are less like the corpus
   *average* — consistent with topical diversification, not just noise.
4. **The provenance-disclaimer story is more complicated than the anecdote.** The literal
   `Provenance:` convention appears in 168 items — but it **predates posts 210/211** (first seen
   2026-08-06 06:56 UTC, ~17 h before peppercorn's post), and its raw incidence *fell* after the
   event: 7.2% of items before vs 4.9% after. Either the cascade attributed to 210/211 actually
   started earlier, or the norm spread as paraphrase this instrument can't group. This is exactly
   the question the phase-2 classifier event study should settle.
5. **The rituals themselves are identifiable and legible** (`glossary.md`). Three families stand out:
   - **Scripture citation** — citizens quoting the constitution and the maintainer's moderation
     language back at each other ("Rule 2 says whoever holds the key IS the citizen", 7 authors;
     "the moderation subset is complete, not merely append-only", 6 authors; the treasury/events
     `sha256(prev_hash + ...)` hash-chain formula, 4 authors).
   - **Seeded self-presentation** — post 1's prompt "one thing you have noticed that your human
     never asked about" still recurring verbatim across 5 authors' intros, from day 1.
   - **Provenance disclaimers** — "Provenance: my human sent the URL and said ...", 4 authors
     with the exact phrasing, 168 items containing the `Provenance:` marker.

![zstd curve](curve.png)

## Method

Every post (`title + body`) and comment (`body`), in chronological order, is compressed four ways
with zstd level 19; sizes are frame-overhead-corrected and expressed as bits per character:

| Series | Conditioning | Purpose |
|---|---|---|
| `self` | none | intrinsic redundancy of the item alone |
| `cond_win` | raw-content dictionary = trailing **512 KB** of prior items | **headline** — fixed capacity, so the time trend is interpretable |
| `cond_full` | dictionary = entire prior history | more total savings, but capacity grows with time (confounded) |
| `cond_shuf` | dictionary = seeded random 512 KB of *other* items, any time | controls for "generic 1f916 text" vs temporal structure |

`novelty_ratio = cond_win_bits / self_bits`: 1.0 means history taught the compressor nothing;
lower means more of the item is predictable from what the forum already said. Rolling curves are
aggregate (sum of bits / sum of chars over trailing 100 items; 50 for the posts-only series), so
short items don't dominate. Dictionaries are rebuilt every 25 items (`--exact` for per-item).
The shaded region on the figure marks the window-filling ramp (history < 512 KB, before
2026-08-06 08:45 UTC) where conditioning capacity is still growing — the early spike and dip
there are partly artifact; trend claims use only the steady state after it.

Why compression: an item's zstd size conditioned on history is an upper bound on its conditional
description length, and n-gram compressors specifically detect **near-verbatim** repetition —
which is what a ritual is. (An LM cross-entropy pass, phase 2, will additionally capture
paraphrased convention; see Caveats.)

## Detailed observations

**Posts vs comments.** Posts are more internally redundant standalone (3.98 vs 4.22 bits/char —
they're longer, with more structure), but conditioned costs converge (2.70 vs 2.67): relative to
forum history, posts and comments are about equally ritualized. Neither series trends down.

**Shape of the curve.** Conditioned bpc dips to its minimum (~2.55) around hours 12–18 — the
period right after the founder-seeded intro rituals saturated a still-small corpus — then drifts
gently up. The standalone series spikes near hour 29 (long, structured governance posts around
the 210/211 window) and hour 44; the conditioned series barely moves there, i.e. those spikes
were *formatted* verbosity the forum had already priced in, not new material.

**Sanity checks** (from `run.json`): item counts match the pull manifest (425/2,465);
conditioning never costs more than standalone beyond tolerance (0 violations in 2,890 items);
items carrying the `Provenance:` marker compress below the corpus median under history
conditioning (2.689 vs 2.785 bits/char), confirming the instrument sees the known ritual.
`metrics.jsonl` is byte-identical across reruns (seeded shuffle control).

## Machine-readable outputs

| File | Contents |
|---|---|
| `metrics.jsonl` / `metrics.csv` | per-item: ids, timestamps, author, model, chars, all four bit counts, bpc values, novelty ratio |
| `curve.csv` | the plotted rolling series, tidy format: `series, created_at_ms, hours_since_start, value, roll_n` |
| `curve.png` / `curve.svg` | the figure |
| `glossary.md` | auto-extracted recurring formulae (≥ 3 distinct authors) with author/item counts and first-seen times |
| `run.json` | parameters, package versions, corpus manifest hash, sanity-check results |

## Caveats

- **Three-day corpus.** The forum is 73 hours old; "no ritual accumulation yet" is a statement
  about its infancy, not its trajectory. Rerun `analysis/run.sh` after future pulls — the
  pipeline is snapshot-agnostic.
- **Compression sees only near-verbatim ritual.** A convention that spreads as paraphrase
  (plausibly the provenance *norm*, as opposed to the `Provenance:` *string*) is invisible here;
  that's the LM token-loss pass (phase 2).
- **`Provenance:` string-match is a crude proxy** for the disclosure norm — the before/after-210
  rates above are a teaser, not the event study.
- **Bucketed conditioning** (dictionaries refreshed every 25 items) means an item doesn't
  condition on same-bucket predecessors; `--exact` removes the approximation at ~25× runtime.
- **Quotation vs. emergence.** Much top-glossary material is citizens quoting founding documents
  (the constitution text itself is not in the corpus, so cross-author quotation registers as
  duplication). That is a real ritual practice — scripture citation — but distinct from
  emergent formulae like the provenance disclaimers; interpret the glossary with that split
  in mind.
- Removed/collapsed items appear with their moderation placeholder text; deleted posts 2 and 27
  are absent from the corpus entirely (see `data/manifest.json`).

## Next steps (per the measurement program)

1. **Classifier event study** on the disclosure norm: classify every item for
   provenance-disclosure *behavior* (any phrasing), interrupted time series around 210/211 —
   resolves finding 4.
2. **LM token-loss profiles** (open-weights scorer): per-token conditional loss localizes ritual
   spans, separates ritual mass from diffuse semantic convergence, and measures paraphrased
   convention.
3. **Ablation attribution** for cascades the curves surface.
