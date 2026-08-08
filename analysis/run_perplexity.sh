#!/usr/bin/env bash
# LM token-loss pass over the corpus, using the local `memetic` conda env
# (torch + transformers) and a model cached on the roomy ~/media drive.
# Extra args pass through to perplexity.py (e.g. --model Qwen/Qwen2.5-14B,
# --window-tokens 4096, --limit 50 for a smoke test).
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="${HF_HOME:-/home/dan/media/hf_cache}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
PY=/home/dan/miniforge3/envs/memetic/bin/python
exec "$PY" analysis/perplexity.py "$@"
