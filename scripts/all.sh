#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
python -m ruff check .
python -m ruff format --check .
python -m bandit -q -r movies web_app.py
python -m pytest --cov --cov-report=term-missing "$@"
