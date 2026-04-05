#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PROFILE="${PROFILE_ID:-v1_demo}"
python main.py verify-delivery --profile-id "$PROFILE"
python main.py export-acceptance-evidence --profile-id "$PROFILE" --output-file "tmp/reports/acceptance_evidence_${PROFILE}.md"
