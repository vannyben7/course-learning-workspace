#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-${TMPDIR:-/tmp}/clw-pycache}"

python3 -m compileall next/course-learning-workspace/app
python3 -m py_compile next/course-learning-workspace/app/server.py
python3 -m unittest discover -s next/course-learning-workspace/tests
node --check next/course-learning-workspace/web/app.js

test -f docs/redesign/course-learning-workspace-v1.md
test -f docs/school-facing/positioning-v1.md
test -f next/course-learning-workspace/docker-compose.yml
test -f next/course-learning-workspace/requirements.txt
test -f scripts/docker-start.sh
test -f scripts/local-start.sh
test -f scripts/clean-local-data.sh

echo "Course Learning Workspace checks passed."
