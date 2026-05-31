#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "${1:-}" != "--yes" ]; then
  echo "This deletes local course files, extracted text, previews, NotebookLM state, and repository-local caches." >&2
  echo "Run: scripts/clean-local-data.sh --yes" >&2
  exit 1
fi

rm -rf \
  "$ROOT_DIR/next/course-learning-workspace/data" \
  "$ROOT_DIR/.academic-os" \
  "$ROOT_DIR/.playwright-cli" \
  "$ROOT_DIR/.venv-build" \
  "$ROOT_DIR/.pytest_cache" \
  "$ROOT_DIR/.ruff_cache" \
  "$ROOT_DIR/.mypy_cache" \
  "$ROOT_DIR/legacy/open-academic-os-v1/local-build-artifacts" \
  "$ROOT_DIR/.DS_Store"

find "$ROOT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +

echo "Local generated data and repository-local caches have been removed."
