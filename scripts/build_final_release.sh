#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PROFILE="${PROFILE_ID:-v1_demo}"
OUT="${OUTPUT_ZIP:-tmp/final_release/cuhksz_gds_${PROFILE}.zip}"
mkdir -p "$(dirname "$OUT")"
python main.py build-release-manifest --profile-id "$PROFILE"
python main.py build-bom --profile-id "$PROFILE"
python main.py build-handover-kit --profile-id "$PROFILE" --output-dir "tmp/handover/${PROFILE}"
python main.py verify-delivery --profile-id "$PROFILE"
python main.py package-final-release --profile-id "$PROFILE" --output-file "$OUT"
echo "Wrote: $OUT"
