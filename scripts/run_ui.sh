#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python main.py run-ui --api-base-url "${UI_API_BASE_URL:-http://127.0.0.1:8000}"
