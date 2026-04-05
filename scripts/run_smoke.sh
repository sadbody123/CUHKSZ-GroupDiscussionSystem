#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python main.py run-smoke \
  --snapshot-id "${SNAPSHOT_ID:-dev_snapshot_v2}" \
  --topic-id "${TOPIC_ID:-tc-campus-ai}" \
  --provider "${PROVIDER:-mock}" \
  --runtime-profile "${RUNTIME_PROFILE:-default}"
