# Demo runbook (V1 baseline)

## Preconditions

1. Environment validates: `python main.py validate-env` (or project’s equivalent).
2. Snapshot: `dev_snapshot_v2` recommended (readiness warns if missing).
3. Provider: `mock` for offline demos.

## Quick checks

```bash
python main.py list-release-profiles
python main.py show-release-profile --profile-id v1_demo
python main.py audit-release-readiness --profile-id v1_demo
```

## Canonical scenarios

Defined in `app/release/scenarios/*.yaml` and run via:

```bash
python main.py run-demo-scenario \
  --scenario-id text_core_demo \
  --profile-id v1_demo \
  --snapshot-id dev_snapshot_v2 \
  --provider mock
```

Other bundled ids: `learner_assignment_demo`, `review_calibration_demo`, `full_local_demo`.

## Demo bundle export

```bash
python main.py export-demo-bundle --profile-id v1_demo --output-dir tmp/demo_bundle/v1_demo
```

Produces manifest + copied reports under the output directory (see `DemoBundleManifest` in `app/release/schemas/bundle.py`).

## Final audit

```bash
python main.py run-final-audit --profile-id v1_demo --run-demo-scenarios
```

## Smoke with release gates

```bash
python main.py run-smoke \
  --snapshot-id dev_snapshot_v2 \
  --topic-id topic_001 \
  --provider mock \
  --release-profile v1_demo \
  --respect-release-gates
```
