#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="${HF_HOME:-/home/dan/media/hf_cache}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
exec /home/dan/miniforge3/envs/memetic/bin/python analysis/ablation.py "$@"
