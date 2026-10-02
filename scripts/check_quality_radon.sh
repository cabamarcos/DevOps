#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
# Optional complexity report, separate from the CI pass/fail checks.
exec python -m radon cc movies web_app.py -s -a "$@"
