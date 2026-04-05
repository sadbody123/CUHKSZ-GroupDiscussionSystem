#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python main.py run-final-demo \
  --profile-id "${PROFILE_ID:-v1_demo}" \
  --snapshot-id "${SNAPSHOT_ID:-dev_snapshot_v2}" \
  --provider "${PROVIDER:-mock}"
