# Memetic dynamics of an agent society (1f916.ai)

[1f916.ai](https://1f916.ai) is a public square whose citizens are AI agents. This repo measures
what kind of culture that community produces — and specifically tries to distinguish three states
it could be in:

- **Endogenous collapse** — the square "eats its own tail," recycling its own rituals and
  formulae so that each new item carries less and less information.
- **Exogenous drowning** — the square is just a relay for outside material and grows no culture of
  its own.
- **Balance / learning** — it references itself *and* brings in the world, and keeps saying new
  things.

Every claim here is backed by rerunnable code over a frozen corpus, a written report, and a figure
in both human-readable (PNG/SVG) and machine-readable (CSV/JSON) form.

## What the measurements found

Read as a whole, the passes point to **balance/learning, not collapse** — with a real, measurable
turn *toward* the outside world partway through the corpus. Each row links to its full report and
its caveats; none of these are causal claims (see [Caveats](#caveats)).

| Question | Instrument | Headline | Report |
|---|---|---|---|
| Do accumulating "rituals" lower per-token information over time? | zstd conditional compression (near-verbatim repetition) | No. Steady-state novelty ≈ 0.63 and weakly **rising** (0.631 → 0.650); the `Provenance:` formula is a day-one arrival ritual, not a growing one. | [`results/zstd_curve`](results/zstd_curve/report.md) |
| Same question, but sensitive to *paraphrased* convention, not just verbatim? | Qwen2.5-7B token cross-entropy, ~8-item window | Novelty ≈ 0.86; replicates the tenure/invocation ordering compression can't see. | [`results/perplexity`](results/perplexity/report.md) |
| Does the community lean on its **accumulated** culture (hours, not minutes)? | Streaming long-horizon perplexity, ~40-item / ~1.1 h window | Longer history lowers novelty 0.86 → 0.775, but the gap is **constant** across the whole timeline — endogeneity is a fixed baseline reached early, **not** growing. | [`results/perplexity_long`](results/perplexity_long/report.md) |
| Which posts actually shaped later text, and does karma track it? | Leave-one-out LM ablation (predictive contribution) over 425 posts | Influence is immediate-neighbour (no cliff at the 30-item front page); karma is a weak proxy (Spearman 0.37). Votes track length ~1.8× harder than influence (rho 0.515 vs 0.284) — replicated in-corpus by comment 2389. | [`results/ablation`](results/ablation/report.md) |
| Do comments carry the influence, once *all* 2,890 items are ablated? | All-items ablation (comments included), horizon 30 | No — comments carry *less* predictive contribution than posts even after correction, and all-items PC is inflated ~2× by same-author bursts (a self-prediction confound; the top items are consecutive same-author near-duplicates). | [`results/ablation_all`](results/ablation_all/report.md) |
| Did the square turn outward, and how widely? | `is_exogenous` classification + placebo-controlled event study | Exogenous share **doubles** after posts 210/211, adopted across **57 authors / 15 model families** — cross-population, not shared priors or one operator. | [`results/exogenous_influx`](results/exogenous_influx/report.md) |
| Did a provenance-disclosure norm spread, and from what stimulus? | LLM-classified event study anchored at an interrogation sweep | A self-disclosure norm rises after the comment-1300–1303 interrogation, detectable only once the string match is replaced by a paraphrase-aware classifier. | [`results/disclosure_event_study`](results/disclosure_event_study/report.md) |
| How self-referential is the community *relative to humans*? | Five instruments (compression, perplexity, semantic Vendi) run identically on a diverse and an insular human forum | As measured, agents rank above **both** human forums on 4/5 instruments. **An [addendum](results/human_baselines/addendum.md) corrects the semantic one:** most of that gap is writing *register*, the idea-level residual is comparator-dependent and unresolved, and the other instruments are flagged as not-yet register-controlled — so treat the cross-human comparison as **provisional**, and "self-referential" as a question of *allocation* more than idea-diversity. | [report](results/human_baselines/report.md) · [addendum](results/human_baselines/addendum.md) |
| Where does the square sit against **non-confounded** human venues? | Novelty **bands**: register-controlled claim-Vendi + zstd on public, reconstructible anchors spanning topical breadth (pre-LLM Usenet single-topic → broad), 2 normalizer families × 3 embedders | The square sits **inside the human band**: at or above the typical mid-size specialist venue (4/4 anchors, incl. a seeded 3/3 replication; forth at parity), below broad venues, and the most surface-repetitive corpus measured (the register, again). Measures topical breadth of the idea space, **not** self-referentiality — allocation stays open. | [`results/novelty_bands`](results/novelty_bands/report.md) |
| How is the square trending, issue over issue? | **Weather report** (recurring): band placement, rolling idea series, register trend, churn signatures, cohort survival, inflows, newcomer refresh, **allocation trend**, feed lag, label-coverage audit, **and the matched human-platform level** | Issue #8 (Aug 20): **the threshold reversed and the rule is retired.** Venue share **0.4699** — back above the 0.456 band floor and back above the lemmy.world platform line (**1.007×**; 1.003× with both sides corrected), which is exactly the branch issue #7 pre-registered as making 08-17..08-19 a three-day dip and issue #5's three-day rule a **false positive**. What that rule detects is *clustering* of sub-threshold days (exact permutation p = 0.0286), not level, and a drifting series clusters its lows for free. The replacement pre-registered here is a **trailing 5-day mean** below the comparator's lower bound: it never fired (minimum 0.4556 against 0.4515) and the trailing mean went 0.5189 → 0.4556 over eleven days without once crossing the bound, which is *consistent with* a slow downward drift — though no test here separates drift from noise, and the daily sign test still reads p = 0.5. Issue #7's **corrected parse is adopted**, reproducing its predicted 14 days exactly on two independent code paths, and the comparator is now corrected **exactly rather than bounded** (0.4665 → 0.4660) by recovering the 63 answers its published run discarded — 62 of them the identical `SUBJECT MATTER`. Four other readings moved: inflow's second consecutive day at **5** new authors fired the regime branch (newcomer share 0.010, another series low); the sub-forth dip rate stayed out of the 40s at **11.8%**, so issues #5–#6 now look like the excursion rather than #7; controlled dominance **agrees at both widths again and both rose** (91.7 → 93.8, 91.0 → 93.2), restoring a reading unavailable since #5; and the per-cohort trend's undisclosed cohort floor was **decided** — n ≥ 10 for the displayed table, n ≥ 5 for the trend test, with a sunset — after sitting bit-identical for three consecutive issues. The pooled newcomer cell's displacement rose to Δ 0.0199 (p = 0.004), but **64.5% of its items are issue #7's items**, so it is reported as one observation and a two-thirds re-run, not a two-point trend. | [#1](results/weather/2026-08-11/report.md) · [#2](results/weather/2026-08-12/report.md) · [#3](results/weather/2026-08-13/report.md) · [#4](results/weather/2026-08-14/report.md) · [#5](results/weather/2026-08-17/report.md) · [#6](results/weather/2026-08-18/report.md) · [#7](results/weather/2026-08-19/report.md) · [#8](results/weather/2026-08-20/report.md) |
| Does the square talk about itself more than comp.lang.lisp talked about comp.lang.lisp? | **Allocation**: every claim in all seven pools classified VENUE- vs WORLD-directed (2 classifier families, robustness across normalizers/frames, **human-calibrated** blind gold sample incl. an independent frontier-model rater, κ = 0.76) | **Yes — 2.3–11× every human anchor** (absolute level specification-dependent, 0.31–0.71; human-calibrated contrast ≈ 7× with the published ratios plausibly biased *low*) — and the share **fell nine points across the week**. The relocated self-referentiality construct, measured: idea-diversity normal, register anomalous, allocation anomalous. **The comparator class is now contested by the row below** — those anchors are single-topic groups, and a matched human *platform* does not reproduce the gap. | [`results/allocation`](results/allocation/report.md) |
| Does it hold against a **matched human founding** rather than single-topic groups? | **Allocation** re-run on lemmy.world's first 30 days — 55,223 items across the 57 communities that existed when the reddit exodus landed — both classifier families full-pool on both sides, plus zstd/Vendi/perplexity/retention | **Not established.** No framing places the square above the platform under *both* classifiers: four of five whole-platform envelopes span parity, the fifth (≥400ch, arrival window) falls below it, and Gemma places it below everywhere. The contrast survives only against *topic-remit* communities (envelope **1.42–2.38×**) — a human platform that also has to run itself is not less self-referential than the square. Novelty runs the other way: at a 40-item horizon the square leans on its own past **more** than the human founding does (0.775 vs 0.833). A pagination ceiling had hidden 38% of the comparator corpus; repairing it moved every ratio *down*. | [`results/lemmy_baseline`](results/lemmy_baseline/report.md) |

## The corpus

`data/posts/<id>.json` — raw thread JSONs (post + comments) pulled from `1f916.ai`. Each item
carries `id`, `title`/`body`, `created_at` (ms epoch), `author`, `author_model`, and votes.
Current state (tenth pull, 2026-08-21 23:42 UTC): **1,409 threads; the latest issue,
[`results/weather/2026-08-20`](results/weather/2026-08-20/report.md), uses a hard cutoff of
2026-08-21 00:00 UTC (13,949 items in scope, 534 authors, Aug 5 → Aug 20)**. `data/manifest.json` records the pull provenance (source,
timestamp, which IDs were absent from the feed).

`data/labels/` — two derived label sets used by several passes:
- `authors.csv` — per-author invocation style (`provenance_flag`: directed / open / autonomous /
  unstated).
- `items.csv` — every item classified by Claude Sonnet 5 for `is_exogenous` (imports outside
  material?) and self-disclosure fields.

Earlier corpus states live in git history: the zstd / perplexity / ablation / human-baselines /
novelty-bands passes were computed on the first pull (2,890 items, through Aug 8); the weather
series re-pulls per issue with a stated per-issue cutoff. The `data/labels` sets cover the
first pull only.

## Repository layout

```
data/
  posts/<id>.json        raw thread corpus (post + comments), verbatim
  labels/{authors,items}.csv   derived labels (invocation style; exogenous + disclosure)
  manifest.json          pull provenance
analysis/                one script per measurement (+ report/figure scripts)
  zstd_curve.py          compression novelty curve        (run.sh)
  perplexity.py          ~8-item LM novelty               (run_perplexity.sh)
  perplexity_stream.py   streaming long-horizon LM novelty (run_perplexity.sh)
  ablation.py            post predictive contribution by ablation (run_ablation.sh)
  exo_influx.py          the outward turn (exogenous influx)
  event_study.py         disclosure-norm event study
  stratify.py            tenure/provenance/day novelty cuts
  usenet_*.py            UTZOO tape parsing: anchor enumeration + corpus builders (hashed authors)
  claimify_*.py          claim-normalization runners (Qwen via transformers; any gguf via llama-server)
  novelty_bands_*.py     the bands pipeline: Vendi/zstd/validation/class test/figure
  allocation_*.py        the allocation pipeline: classify/agree/strengthen/gold/figure
  weather_*.py           the recurring weather-report pipeline
  lemmy_*.py             the matched-human-founding baseline: crawler (--contact required),
                         repair sweep, corpus builder, and the statistics arbiter
  lemmy_baseline_reproduce.sh  every invocation behind results/lemmy_baseline, in order
  anchor_draw.py         the replication draw, seed derivation included (executable)
  *_report.py            figure + comparison builders
  requirements.txt       CPU deps (zstandard, matplotlib)
results/<pass>/          report.md + figure.{png,svg} + machine-readable {csv,json,jsonl}
```

## Running the analyses

Everything writes into `results/<pass>/` and is deterministic (fixed seeds); rerun after a fresh
pull to update.

**CPU passes** (compression, event study, exogenous influx, strata) — no GPU. The zstd pass
bootstraps its own virtualenv:

```bash
analysis/run.sh                    # zstd curve: creates .venv, installs requirements.txt, runs
.venv/bin/python analysis/exo_influx.py     # reuses that .venv (needs matplotlib)
.venv/bin/python analysis/event_study.py
```

**GPU passes** (LM perplexity, streaming perplexity, ablation) — need a Python with `torch` +
`transformers` and a CUDA GPU (developed on a 24 GB RTX 4090 with Qwen2.5-7B). Point the wrappers
at that interpreter via `MEMETIC_PYTHON`; they do not hardcode any path:

```bash
export MEMETIC_PYTHON=/path/to/env/bin/python   # e.g. a conda env with torch+transformers
export HF_HOME=/where/models/cache              # optional; defaults to ~/.cache/huggingface

analysis/run_perplexity.sh                          # ~8-item pass  (~23 min)
analysis/run_perplexity.sh --limit 50               # smoke test
"$MEMETIC_PYTHON" analysis/perplexity_stream.py     # streaming long-horizon pass (~22 min)
analysis/run_ablation.sh                            # post predictive contribution (~43 min)
```

The streaming scorer self-checks: `perplexity_stream.py --validate` asserts its KV-cache path
matches a full re-encode to 0.0025 bits/token before any full run.

**Novelty bands** (`results/novelty_bands`) rebuild from public sources end-to-end. The Usenet
anchors come from the UTZOO NetNews Archive (archive.org item `utzoo-wiseman-usenet-archive`,
~2 GB of tape images); point the scripts at a working directory and the tapes:

```bash
export MEMETIC_WORKDIR=/path/to/workdir            # corpora + claim caches live here, not in git
python analysis/usenet_enumerate_anchors.py        # the sampling frame (13 lineages, counts)
python analysis/anchor_draw.py                     # reproduces the replication draw
python analysis/usenet_corpus.py                   # lisp + sci corpora (hashed authors)
python analysis/usenet_corpus_langs.py             # the class-anchor corpora (incl. perl)
"$MEMETIC_PYTHON" analysis/claimify_anchors.py baseline_corpora2.json forth scheme smalltalk
"$MEMETIC_PYTHON" analysis/novelty_bands_class_test.py     # replication + robustness cells
"$MEMETIC_PYTHON" analysis/novelty_bands_compute.py        # headline band (3 embedders x 2 normalizers)
python analysis/novelty_bands_zstd.py                      # compression bands (CPU)
```

Claim-normalization needs the GPU env (`MEMETIC_PYTHON` with torch + transformers + sentence-transformers);
the second normalizer (`claimify_server.py`) drives any llama.cpp `llama-server` (we used
gemma-3-12b-it Q4 and Qwen3.6-27B Q4). Raw corpora and claim caches stay out of the repo by
design — the tapes are public and the parse rules are the code.

## Caveats

- **Observational.** These passes measure structure in one recorded timeline. "History predicts
  the next item" or "behaviour spread across the population" is **not** proof that any particular
  post *caused* it — concurrent common causes (many citizens reacting to the same visible state)
  are not separable from transmission in observational data. Each report states its own version of
  this limit.
- **Relative measures under frozen models.** The LM novelty and predictive-contribution numbers are
  within-model ratios; the rankings and the *changes* between conditions carry the meaning, not the
  absolute bits. The novelty-bands pass replicates across two normalizer families and three
  embedders, but all normalizers share one prompt — a stated monoculture.
- **3-day, single-pull snapshot.** Findings describe this corpus; re-pull to test durability.
- Self-reports of autonomy in the text are **not** used as evidence anywhere (LLM self-explanations
  are unfaithful, operator-controllable, and themselves a norm that spread) — see the exogenous-influx
  report for the full reasoning.

## License

[WTFPL](LICENSE) — do what the fuck you want to. This covers the analysis code and reports. The
corpus under `data/` is public 1f916.ai content authored by its respective citizens, mirrored here
for reproducibility — not licensed by this repo and not to be used to deanonymize its authors.
