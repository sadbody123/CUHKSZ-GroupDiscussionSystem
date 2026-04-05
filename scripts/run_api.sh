#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python main.py run-api --host 127.0.0.1 --port 8000
