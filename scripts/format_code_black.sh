#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
# Compatibility entrypoint: formatting is now consolidated in Ruff.
exec python -m ruff format . "$@"
