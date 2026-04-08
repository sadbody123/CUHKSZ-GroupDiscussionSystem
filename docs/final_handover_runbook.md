# Final Handover Runbook

Use this runbook for demo day, handover, and acceptance walkthrough.

## 1. Recommended Setup

```bash
python -m pip install -e ".[dev,graph]"
python main.py bootstrap-dev-snapshot
```

## 2. Start Services

Terminal A (backend):

```bash
python main.py run-api --host 127.0.0.1 --port 8000
```

Terminal B (frontend):

```bash
cd frontend
npm install
npm run codegen:openapi
npm run dev
```

Optional Terminal C (Streamlit legacy UI):

```bash
python main.py run-ui --api-base-url http://127.0.0.1:8000
```

## 3. Demo Sequence (Recommended)

1. Open Discussion Console (`/sessions`)
2. Create session from `dev_snapshot_v2`
3. Enter session detail
4. Submit a user turn
5. Run next turn
6. Show transcript pagination and runtime timeline panel
7. Open Runtime Reviews (`/runtime-reviews`) if review item exists
8. Apply edited draft or approve/resume
9. Return to session detail and show linkage

## 4. Validation Commands

### Baseline

```bash
python -m pytest -m "not v2_graph" -q
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
```

### Full

```bash
python -m pytest -q
cd frontend
npm run test
npm run build
npm run e2e:mock
npm run e2e:real
```

## 5. Demo Troubleshooting

- Session create fails:
  - verify `dev_snapshot_v2` exists (`bootstrap-dev-snapshot`)
- V2 behavior missing:
  - verify `AGENT_RUNTIME_BACKEND=v2` for V2-specific demonstrations
- Codegen mismatch:
  - rerun `npm run codegen:openapi`
- Playwright real mode fails:
  - ensure ports `8000` and `4173` are free

## 6. Handover Checklist

- [ ] Minimal mode commands validated
- [ ] Full mode commands validated
- [ ] Discussion path demonstrated
- [ ] Review path demonstrated
- [ ] Transcript/timeline endpoints verified
- [ ] Known limitations reviewed (`KNOWN_LIMITATIONS_FINAL.md`)
