#!/usr/bin/env bash
# Rerun the zstd ritual-accumulation analysis over the corpus in data/.
# Bootstraps a local venv on first use. Extra args are passed through to
# zstd_curve.py (e.g. --exact, --level 12, --window-bytes 1048576).
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r analysis/requirements.txt
exec .venv/bin/python analysis/zstd_curve.py "$@"
