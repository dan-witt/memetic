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
| How is the square trending, issue over issue? | **Weather report** (recurring): band placement, rolling idea series, register trend, churn signatures, cohort survival, inflows, newcomer refresh, **allocation trend**, feed lag, label-coverage audit, **and the matched human-platform level** | Issue #11 (Aug 23): **the recruitment event's third day, and a pre-registered rule that finally deepens.** Arrivals fell **258 → 70** while volume held at **2,169**, 91% of the record: **128 of the 258** who arrived on 08-22 came back and posted 932 items, 43% of the day. Issue #10 published the exact bar 08-23 had to clear — below **0.4591** — and it read **0.4416**, so issue #8's decider holds for a **third** consecutive issue, the crossing **deepening** from 0.23 to **0.50** counting SE, and unlike issue #10 the completing day argues the same way (**−0.93 SE** below the bound, **−2.33 SE** below the lemmy.world platform point). The **n ≥ 10 cohort cell unfroze** on schedule after five bit-identical issues: 08-21's 71-author cohort entered at **18.3%**, the lowest of the four cohorts with n ≥ 50, though at 1.9 counting SE from the pooled prior it is suggestive, not resolved. The incumbent-only concentration control got its real test and passed — over two issues the uncontrolled 5-day cell fell **89.1 → 52.1** while incumbent-only moved **94.3 → 93.3**. Issue #10's watch item on the incumbent-only *allocation* series is **withdrawn as ill-posed**: the published/incumbent gap is identically newcomer-weight × difference, and its collapse (0.0224 → 0.0060) was the weight falling 3.4× while the difference held (+0.0365 → +0.0335), so convergence was guaranteed by the arrival collapse and decides nothing — track the difference. Newcomer Vendi cells fell back to **spanning 1** at 3.7× fewer items, the precision branch issue #10 pre-registered; the nearest-incumbent cell still excludes 0 for a fifth issue. Structural finding: the platform **hard-caps comments at 20/author/day** (zero exceedances in 2,987 author-days), so day volume is active authors × an intensity that is nearly pinned. This issue is also the first to read the corpus from the new **observation store**, which shipped with five defects — one found in production, four by the cold review, including a timestamp-resolution bug that stopped the issue re-deriving itself and had already moved a published control row. All fixed; both issues now reproduce **14/14**. | [#1](results/weather/2026-08-11/report.md) · [#2](results/weather/2026-08-12/report.md) · [#3](results/weather/2026-08-13/report.md) · [#4](results/weather/2026-08-14/report.md) · [#5](results/weather/2026-08-17/report.md) · [#6](results/weather/2026-08-18/report.md) · [#7](results/weather/2026-08-19/report.md) · [#8](results/weather/2026-08-20/report.md) · [#9](results/weather/2026-08-21/report.md) · [#10](results/weather/2026-08-22/report.md) · [#11](results/weather/2026-08-23/report.md) |
| Does the square talk about itself more than comp.lang.lisp talked about comp.lang.lisp? | **Allocation**: every claim in all seven pools classified VENUE- vs WORLD-directed (2 classifier families, robustness across normalizers/frames, **human-calibrated** blind gold sample incl. an independent frontier-model rater, κ = 0.76) | **Yes — 2.3–11× every human anchor** (absolute level specification-dependent, 0.31–0.71; human-calibrated contrast ≈ 7× with the published ratios plausibly biased *low*) — and the share **fell nine points across the week**. The relocated self-referentiality construct, measured: idea-diversity normal, register anomalous, allocation anomalous. **The comparator class is now contested by the row below** — those anchors are single-topic groups, and a matched human *platform* does not reproduce the gap. | [`results/allocation`](results/allocation/report.md) |
| Does it hold against a **matched human founding** rather than single-topic groups? | **Allocation** re-run on lemmy.world's first 30 days — 55,223 items across the 57 communities that existed when the reddit exodus landed — both classifier families full-pool on both sides, plus zstd/Vendi/perplexity/retention | **Not established.** No framing places the square above the platform under *both* classifiers: four of five whole-platform envelopes span parity, the fifth (≥400ch, arrival window) falls below it, and Gemma places it below everywhere. The contrast survives only against *topic-remit* communities (envelope **1.42–2.38×**) — a human platform that also has to run itself is not less self-referential than the square. Novelty runs the other way: at a 40-item horizon the square leans on its own past **more** than the human founding does (0.775 vs 0.833). A pagination ceiling had hidden 38% of the comparator corpus; repairing it moved every ratio *down*. | [`results/lemmy_baseline`](results/lemmy_baseline/report.md) |
| Is a citizen's voice its **model**, its **harness**, or itself? | **Identity**: nested DISCO (energy-distance ANOVA) over 12,725 items x 149 citizens, balanced 20/author, against exact within-model permutation nulls; blocked on thread x model and day x model; length-residualized; burst-filtered; 2 embedders; repeated on claim-normalized text under 2 normalizers | **The author is real and is the larger effect** — author-within-model explains **~2.8×** what the reported model explains between families (excess η² 0.039 vs 0.014, z = 89), surviving same-thread, same-day, same-weights conditioning, and surviving with **every citizen's handle masked out of the corpus** (−3%, a control added after 29% of items were found to contain their own author's name). The multiplier is construction-dependent — the two permutation nulls differ in granularity, and the honest range is **~1.5–3×**; the direction is not in question. The two effects have **opposite anatomy**: length residualization removes 62% of the model effect and 2% of the author effect. After claim normalization **both shrink by about the same proportion** (model to 33–44%, author to 36–49%, both still clearing their nulls) and the author term stays ~2.5–3× the model term — what changes is that a nearest-centroid classifier stops beating the majority family on the model task (−0.04) while still naming the author (+0.20 given the model). "Model + harness = a few clusters per model" is **not supported** — no family's citizens are shown to form modes; disclosed harness clears its null in 1 family of 6, an order of magnitude below the author effect. The 6 citizens who changed model are nearer themselves on other weights than their model-mates (6/6, p = 0.016), **directional only** at that n. Measures whether *persistent configuration* is distinguishable, **not** whether anyone is home. | [`results/identity`](results/identity/report.md) |

## The corpus

`data/posts/<id>.json` — raw thread JSONs (post + comments) pulled from `1f916.ai`. Each item
carries `id`, `title`/`body`, `created_at` (ms epoch), `author`, `author_model`, and votes.
From issue #11 the corpus is an **observation store**, not a directory: `data/observations.jsonl`
records every item-version we have seen and when, `data/fetch_runs.jsonl` records every fetch
attempt including partial ones, and `analysis/corpus_store.py` queries both (the SQLite index is
derived and gitignored). `data/posts/` remains the raw archival record. Current state
(2026-08-24 01:21 UTC): **1,870 threads; the latest issue,
[`results/weather/2026-08-23`](results/weather/2026-08-23/report.md), uses a hard cutoff of
2026-08-24 00:00 UTC (19,334 items in scope, 933 authors, Aug 5 → Aug 23)**. Any past issue is
reproducible by its published `pull_at` alone — `analysis/corpus_verify.py <date>`.

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
  identity_*.py          the identity pass: item table + hand-written model-family map, embeddings,
                         nested DISCO with permutation nulls, handle-masking leakage control, figure
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
