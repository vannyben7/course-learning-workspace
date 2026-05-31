#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT_DIR/next/course-learning-workspace"

cd "$APP_DIR"
docker compose up -d --build

echo "Course Learning Workspace Docker is running:"
echo "http://${CLW_BIND_IP:-127.0.0.1}:${CLW_HOST_PORT:-8780}"
