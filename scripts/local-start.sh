#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT_DIR/next/course-learning-workspace"
VENV_DIR="${CLW_VENV_DIR:-$ROOT_DIR/.venv}"
HOST="${CLW_HOST:-127.0.0.1}"
PORT="${CLW_PORT:-8780}"
DATA_DIR="${CLW_DATA_DIR:-$APP_DIR/data}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required. Set PYTHON_BIN=/path/to/python3 if needed." >&2
  exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

mkdir -p "$DATA_DIR"

echo "Course Learning Workspace local server:"
echo "http://$HOST:$PORT"
echo "Data directory: $DATA_DIR"

cd "$APP_DIR"
exec env \
  CLW_HOST="$HOST" \
  CLW_PORT="$PORT" \
  CLW_DATA_DIR="$DATA_DIR" \
  PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-${TMPDIR:-/tmp}/clw-pycache}" \
  "$VENV_DIR/bin/python" -m app.server
