#!/usr/bin/env bash
# Exact invocations behind every number in results/lemmy_baseline/report.md, in dependency order.
# The orchestration that actually ran lives in the working directory (chain4.sh / chain4b.sh) and
# is not committed; this is the committed record of WHAT was run, so the report's artifacts can be
# regenerated without reading a shell history.
#
# THREE INTERPRETERS ARE REQUIRED and they are not interchangeable:
#   $GPY   conda `memetic`, Python 3.9  — torch + transformers + sentence_transformers (GPU work)
#   $PY    system python3.12            — the stats arbiter (needs 3.10+ syntax)
#   $VPY   repo .venv, python3.12       — zstd (needs BOTH 3.10+ syntax and the zstandard module;
#                                          the conda env has zstandard but is 3.9, system 3.12 has
#                                          the syntax but not the module)
#
# Usage: lemmy_baseline_reproduce.sh <step|all>     steps: crawl corpus qwen gemma stats vendi zstd ppl
set -u
export MEMETIC_WORKDIR=${MEMETIC_WORKDIR:-/home/dan/personal/memetic-workdir}
W=$MEMETIC_WORKDIR; R=/home/dan/personal/memetic
GPY=/home/dan/miniforge3/envs/memetic/bin/python
PY=python3
VPY=$R/.venv/bin/python
LLAMA=/home/dan/media/models/llamacpp/llama-b10344/llama-server
GGUF=/home/dan/media/models/gemma-3-12b-it-Q4_K_M.gguf
STEP=${1:?step required: crawl|corpus|qwen|gemma|stats|vendi|zstd|ppl|all}

server_up(){ nohup "$LLAMA" -m "$GGUF" --host 127.0.0.1 --port 8089 -c 32768 --parallel 16 \
    -ngl 99 -fa on --device Vulkan0 -b 2048 -ub 512 > "$W/lemmy/gemma_server.log" 2>&1 &
  until curl -s -m 2 http://127.0.0.1:8089/v1/models | grep -q '"data"'; do sleep 5; done; }
server_down(){ local p; p=$(pgrep -x llama-server|head -1); [ -n "${p:-}" ] && kill "$p"; sleep 5; }

run_crawl(){    # -> lemmy/{posts,comments}.jsonl   NOT part of `all`: multi-day at Crawl-delay 60
  : "${MEMETIC_CONTACT:?set MEMETIC_CONTACT to your own reachable address before crawling}"
  cd "$R" && $PY analysis/lemmy_crawl.py --contact "$MEMETIC_CONTACT"
  cd "$R" && $PY analysis/lemmy_crawl_repair.py --contact "$MEMETIC_CONTACT"; }

run_corpus(){   # -> baseline_corpora_lemmy.json (63,985 records)
  cd "$R" && $PY analysis/lemmy_corpus.py; }

run_qwen(){     # -> baseline_claims/lemmy_all.json, allocation_labels_lemmy.json
  cd "$R" && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    $GPY analysis/claimify_anchors.py baseline_corpora_lemmy.json lemmy
  cd "$R" && ALLOC_SUFFIX="_lemmy" PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    $GPY analysis/allocation_run.py lemmy; }

run_gemma(){    # -> baseline_claims_gemma/lemmy_all.json, allocation_agree_pairs_lemmy_full.json
  server_up
  # Resumes from {pool}_partial.json when a sidecar signature matches the item sequence; a
  # checkpoint predating sidecars is adopted only via claimify_resume_verify.py (see its header).
  cd "$R" && CLAIMIFY_WORKERS=16 $PY analysis/claimify_server.py 8089 baseline_claims_gemma lemmy
  cd "$W" && ALLOC_LABELS=allocation_labels_lemmy.json ALLOC_SUFFIX=_lemmy_full ALLOC_NSAMPLE=200000 \
    $PY "$R/analysis/allocation_agree.py" lemmy
  server_down; }

run_stats(){    # -> results/lemmy_baseline/results.json (the arbiter; 88 intervals)
  cd "$R" && $PY analysis/lemmy_baseline_stats.py --draws 3000; }

run_vendi(){    # -> band_final_v3.json  (six agent/lemmy cells, §7.1)
  cd "$R" && BAND_SUFFIX="_v3" BAND_POOLS="agentcur,hn,lisp,sci,lemmy" \
    $GPY analysis/novelty_bands_compute.py; }

run_zstd(){     # -> band_zstd_lemmy3.json  (§7.1 table)
  cd "$R" && $VPY analysis/novelty_bands_zstd.py band_zstd_lemmy3.json baseline_claims \
    agentcur lemmy lisp sci forth scheme; }

run_ppl(){      # -> lemmy/perplexity_long/  (§7.1 long-window row)
  # 15000/18000 match the agent long-window run (results/perplexity_long) so the rows compare.
  # --limit 2890 is the founding window, which sits inside the byte-identical pre-repair corpus
  # prefix (diverges at item 8,062), so the pre-repair forum view is valid input here.
  cd "$R" && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    $GPY analysis/perplexity_stream.py \
      --data-dir "$W/lemmy_forumview/posts" --out-dir "$W/lemmy/perplexity_long" \
      --window-tokens 15000 --cap 18000 --limit 2890; }

case "$STEP" in
  crawl) run_crawl ;; corpus) run_corpus ;; qwen) run_qwen ;; gemma) run_gemma ;; stats) run_stats ;;
  vendi) run_vendi ;; zstd) run_zstd ;; ppl) run_ppl ;;
  all) run_corpus && run_qwen && run_gemma && run_vendi && run_zstd && run_ppl && run_stats ;;
  *) echo "unknown step: $STEP" >&2; exit 1 ;;
esac
