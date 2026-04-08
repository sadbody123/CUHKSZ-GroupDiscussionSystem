# Quickstart

## Minimal (V1-first)

```bash
python -m pip install -e ".[dev]"
python main.py bootstrap-dev-snapshot
python -m pytest -m "not v2_graph" -q
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
```

## Full (V2 fullstack)

```bash
python -m pip install -e ".[dev,graph]"
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm install
npm run codegen:openapi
npm run test
npm run build
npm run e2e:mock
npm run e2e:real
```

For full walkthrough and demo sequence, see `docs/final_handover_runbook.md`.
