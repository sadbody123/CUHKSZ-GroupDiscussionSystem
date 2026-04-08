# Local Runbook (Release Freeze)

## 1) Environment Modes

### Minimal / V1-first

```bash
python -m pip install -e ".[dev]"
```

Use this mode for:

- baseline API/CLI checks
- V1-first testing without LangGraph dependency

### Full / V2 fullstack

```bash
python -m pip install -e ".[dev,graph]"
```

Use this mode for:

- V2 graph runtime tests
- frontend + codegen + Playwright

## 2) Bootstrap Data

```bash
python main.py bootstrap-dev-snapshot
```

This ensures `dev_snapshot_v2` exists in snapshot root.

## 3) Backend Startup

```bash
python main.py run-api --host 127.0.0.1 --port 8000
```

Optional Streamlit:

```bash
python main.py run-ui --api-base-url http://127.0.0.1:8000
```

## 4) Frontend Startup

From `frontend/`:

```bash
npm install
npm run codegen:openapi
npm run dev
```

## 5) Functional Walkthrough

1. Open `/sessions`
2. Create session with `dev_snapshot_v2` + a topic
3. Enter session detail
4. Submit user turn
5. Run next turn or auto run
6. Inspect transcript and runtime timeline
7. If review generated, open `/runtime-reviews` and process item

## 6) Test Commands

### Baseline

```bash
python -m pytest -m "not v2_graph" -q
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
```

### Full

```bash
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm run codegen:openapi
npm run test
npm run build
npm run e2e:mock
npm run e2e:real
```

## 7) Troubleshooting

- `langgraph not installed`: switch to minimal test command or install `.[graph]`.
- Missing snapshot/topic: rerun `python main.py bootstrap-dev-snapshot`.
- Codegen output missing: run `cd frontend && npm run codegen:openapi`.
- Real E2E failures: verify backend port `8000` is free and frontend port `4173` is available.
