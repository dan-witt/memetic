# Endogeneity under a language model — the perplexity pass

*Corpus: 2,890 items, 1f916.ai. Scorer: **Qwen2.5-7B** (base), frozen, run locally on an
RTX 4090 (torch 2.1.1 / transformers 4.45, `memetic` conda env). Full coverage in ~23 min
(2.2 items/s). Pipeline: `analysis/perplexity.py` (rerun: `analysis/run_perplexity.sh`);
figure/strata: `analysis/perplexity_report.py`. This is step 2 of the measurement program —
the LM analogue of the zstd curve, sensitive to paraphrase, not just verbatim repetition.*

## What this measures and why it matters

Each item is scored twice under the frozen 7B: **self** (the item alone) and **cond** (the item
after a 3,072-token trailing window of forum history). Per-token loss in bits; the self→cond
drop is the LM novelty ratio. The point of doing this after zstd: a compressor only detects
*near-verbatim* ritual, so it is blind to a convention that spreads as **paraphrase** — semantic
convergence without shared phrasing, which is the more dangerous collapse precursor. The LM sees
both. So this pass is the test of whether the zstd study's anti-collapse conclusion survives a
paraphrase-sensitive instrument.

## Headline: the anti-collapse reading is robust to the instrument

**Both instruments say novelty is flat-to-rising, not falling.** Steady-state (after the
window fills, ~hour 14):

| | LM (Qwen2.5-7B) | zstd |
|---|---|---|
| novelty ratio (cond/self) | 0.83 | 0.64 |
| trend | **+0.0084 / day** | +0.0074 / day |
| by day (Aug 6→7→8) | 0.812 → 0.841 → 0.826 | (rising) |

The two curves agree on direction — the community is not losing per-token information over its
first three days, under *either* a verbatim compressor or a model that catches paraphrase. If
anything the paraphrase-sensitive instrument sees slightly *more* novelty growth. In the
collapse/drowning/learning frame this is a second, independent vote against endogenous collapse.

**The levels differ, and the difference is the point.** The LM's standalone description length
(1.22 bits/char) is already far below zstd's (4.2), because a 7B models AI-agent forum prose well
without any forum history — so forum conditioning buys it less *relative* gain (14% vs zstd's
36%). Absolute reduction: 0.17 bits/char (LM) vs 1.48 (zstd). The LM is the better model; the
history teaches it less because it already knew most of it.

**The two novelty measures correlate only 0.33 across items** — they are genuinely different
lenses. Where they diverge (an item zstd calls novel but the LM finds predictable) is
paraphrased convention the compressor missed; those items are extractable from the joined
metrics and are the natural seed for a "semantic convergence" probe.

## The LM independently replicates every zstd stratification

This is the strong corroboration: the patterns the zstd study found are **not compression
artifacts** — a different instrument reproduces them.

- **Provenance-brief ordering, same direction:** directed 0.855 < open 0.881 < autonomous 0.895.
  Directed-brief agents write the most history-predictable text; open/autonomous the least —
  exactly the zstd finding, now confirmed on paraphrase. The society's exogenous injection
  arrives disproportionately through open-brief entrants under both measures.
- **First-item novelty peak:** item-tenure 0.913 (1st) → 0.844 (6–10) → 0.861 (11+) — the same
  shallow assimilation gradient, with newcomers arriving most novel.
- **Posts > comments:** 0.922 vs 0.845 — posts carry the fresh thought, comments do the
  assimilated conversational labor. Same split as zstd.

## Ritual mass

Low-information tokens (conditioned loss < 1 bit/token) are **21.3%** of steady-state tokens —
the LM's ritual-mass estimate, comparable in spirit to the zstd glossary but token-localized and
paraphrase-inclusive. Per-token conditioned bits are stored in `tokens.npz` (float16 +
per-item offsets), so ritual spans can be highlighted and read out without re-scoring — the
input to the ritual-span deep dive and a cross-check on the zstd glossary.

## Outputs

| File | Contents |
|---|---|
| `metrics.jsonl` / `.csv` | per-item: self/cond bits per token & char, novelty ratio, low-info fraction, window size |
| `tokens.npz` | per-token conditioned bits (float16, concatenated) + per-item index — for ritual-span localization |
| `figure.png` / `.svg` | LM standalone vs conditioned bits/char; LM vs zstd novelty |
| `strata.json` | tenure, provenance, posts/comments cuts |
| `run.json` | model, params, versions, timing, sanity checks |

## Caveats

- **A 7B is a strong but imperfect scorer.** It models this register well (that's why standalone
  loss is low), but a larger model would condition on distal history more effectively and might
  read a slightly different novelty level. The *relative* measurements (trends, strata, ablation
  deltas) are robust to model choice; the absolute novelty level is not. A 14B/32B spot-check on
  a sample would quantify this — deferred, since the direction-of-trend result is what matters
  and it already agrees with zstd.
- **This is a LOCAL endogeneity measure — the conditioning window is only ~8 items.** 3,072
  tokens at ~400 tokens/item holds just ~8 prior items, so "conditioned on forum history" really
  means "conditioned on the immediately preceding ~8 items." A slow, global convergence spread
  over hundreds of items (the textbook echo-chamber-collapse shape) would **not** register in
  this pass — an item is only compared against its recent neighborhood. So the flat-to-rising
  novelty result is strong evidence against *local* collapse; it is weaker evidence about
  *global* drift. Re-running at a larger window (8K–24K ≈ 20–60 items) is the way to probe
  longer-range endogeneity, and is exactly the horizon the ablation pass now sweeps (30/60 items).
- **3-day corpus; single pull.** Same as every other pass here — rerun after future pulls.
- **No significance test on the trend.** The +0.0084/day slope is a point estimate on a 3-day,
  single-society sample; it says "not falling," not "significantly rising."
- **Base vs instruct:** the base model was used for clean LM perplexity (no chat-template
  priors). An instruct model would shift absolute levels, not the trends.

## Follow-ups to circle back to

Deferred from this pass, in rough priority order:

1. **Larger-window rerun (global endogeneity).** Re-score at W=8K–24K (≈20–60 items) to test
   whether the flat-to-rising novelty holds at longer range, or whether a slow global
   convergence hides below the ~8-item local horizon. Cheap (~20–40 min); the single most
   important gap. Partially addressed as a side effect of the 30/60-item ablation baselines.
2. **LM ritual glossary from `tokens.npz`.** The per-token conditioned bits are stored but not
   yet read out — extract the lowest-loss contiguous spans (the LM's "most predictable from
   history" text) and cross-check against the zstd verbatim glossary. Where the LM flags a span
   the compressor didn't, that's paraphrased ritual.
3. **Characterize the LM↔zstd divergence (corr 0.33).** Pull the items zstd calls novel but the
   LM finds predictable — these are paraphrased convention / semantic convergence invisible to a
   compressor. This is the paraphrase-collapse detector the whole LM pass was motivated by; it
   deserves its own short analysis rather than a one-line correlation.
4. **Larger-model spot-check (14B/32B).** Confirm the absolute novelty level and the strata
   orderings on a sample — the trends should be model-robust, the levels won't be.
5. **Per-model-cohort curves.** Stratify novelty by `author_model` (claude-fable-5 dominates, but
   thin non-Claude cohorts exist) to separate shared-prior convergence from transmission — the
   original null-model concern.

## Next: ablation / clout

The clout pass ablates each **post** (425, the considered thoughts — not all 2,890 items),
measuring downstream loss degradation at horizons of **30 and 60 items** (the front page shows
30 — the test is whether clout falls off a cliff at that visibility boundary). Per ablated post,
the X-deleted context is built once and extended across the affected items via KV-cache reuse
(the tail→head sweep keeps the shared prefix resident rather than rebuilding it), so full
coverage at these horizons is ~20–45 min rather than the ~2–11 h a naive per-item rebuild would
cost. The 60-item (~24K-token) horizon requires `attn_implementation="sdpa"` to fit in 24 GB.
Deliverable includes the `corr(karma, clout)` test: the prediction is that this society's own
vote signal is decoupled from computational influence — if so, that decoupling is the finding,
and the reason the computational reward function has to exist.
