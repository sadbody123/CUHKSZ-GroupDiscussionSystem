# Demo Script (Freeze)

## Recommended mode

Use full mode for demo:

```bash
python -m pip install -e ".[dev,graph]"
python main.py bootstrap-dev-snapshot
python main.py run-api --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run codegen:openapi
npm run dev
```

## Demo sequence

1. Open `/sessions`
2. Create session (`dev_snapshot_v2`)
3. Submit user turn and run next turn
4. Show transcript and runtime timeline
5. Open `/runtime-reviews` and process a review item if available
6. Return to session detail via linkage

## Validation commands (optional during demo prep)

```bash
python -m pytest -q
cd frontend
npm run test
npm run build
npm run e2e:mock
```

See `docs/final_handover_runbook.md` for full handover checklist.
