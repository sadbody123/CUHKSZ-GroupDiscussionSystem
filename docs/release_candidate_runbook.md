# Release candidate runbook (local)

## 1. Environment

```bash
python main.py validate-env
```

## 2. Consistency

```bash
python main.py run-consistency-audit --profile-id v1_demo
```

## 3. E2E matrix (mock)

```bash
python main.py run-e2e-matrix --profile-id v1_demo --snapshot-id dev_snapshot_v2 --provider mock
```

## 4. Stability + RC

```bash
python main.py show-stability-report --profile-id v1_demo
python main.py build-rc-report --profile-id v1_demo
```

## 5. Final regression bundle

```bash
python main.py run-final-regression --profile-id v1_demo
```

## 6. Smoke with stability (optional)

```bash
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id topic_001 --provider mock \
  --release-profile v1_demo --respect-release-gates --with-stability-audit
```
