#!/usr/bin/env bash
# LM token-loss pass over the corpus, using the local `memetic` conda env
# (torch + transformers) and a model cached on the roomy ~/media drive.
# Extra args pass through to perplexity.py (e.g. --model Qwen/Qwen2.5-14B,
# --window-tokens 4096, --limit 50 for a smoke test).
set -euo pipefail
cd "$(dirname "$0")/.."
# Cache models wherever HF_HOME points (defaults to HF's own ~/.cache/huggingface).
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
# Python with torch + transformers installed. Override with MEMETIC_PYTHON=/path/to/bin/python
# (e.g. a conda env); otherwise falls back to whatever `python3` is on PATH.
PY="${MEMETIC_PYTHON:-python3}"
exec "$PY" analysis/perplexity.py "$@"
