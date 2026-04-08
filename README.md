# CUHKSZ Group Discussion System

Offline-first group discussion training system with:

- Python/FastAPI backend
- V1 runtime (default)
- V2 runtime (LangGraph-based, optional)
- Streamlit UI (legacy UI surface, still supported)
- React + TypeScript console (Discussion + Runtime Review)

This repository is a local engineering/research delivery, not a production SaaS platform.

## What Is Included In This Delivery

- Session discussion flow: create session, submit user turn, run next, auto run, feedback
- V2 quality branch: pass/repair/interrupt and review queue workflow
- Runtime review operations: approve/reject/resume/apply edited draft
- Transcript API and runtime timeline API
- OpenAPI codegen pipeline for frontend contracts
- Playwright E2E in two modes:
  - mock route mode
  - real-backend mode
- CI matrix:
  - baseline (minimal/V1-first)
  - full-v2-fullstack

## Delivery Status Classification

### Stable in this freeze

- V1 default runtime path and baseline smoke/test flow
- V2 discussion + review workflow (opt-in backend)
- Transcript API and runtime timeline API
- Discussion Console and Runtime Review Console
- OpenAPI codegen and frontend adapter-based contract layer
- CI baseline/full-v2-fullstack matrix

### Optional / environment-dependent

- V2 graph runtime execution (`AGENT_RUNTIME_BACKEND=v2`)
- LangGraph-dependent pytest suite (`v2_graph`)
- Playwright real-backend E2E mode

### Post-freeze enhancements (not part of this delivery)

- Real-backend review E2E deeper mutation coverage
- Full removal of residual manual DTO transition surfaces
- Advanced timeline visualization and analytics UI
- Stronger distributed persistence model for review/checkpoint/event stores

## Official Runtime Modes

### 1) Minimal / V1-first (no LangGraph required)

Recommended for quick local bring-up and baseline verification.

```bash
python -m pip install -e ".[dev]"
python main.py bootstrap-dev-snapshot
python -m pytest -m "not v2_graph" -q
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
```

### 2) Full / V2 fullstack

Recommended for full delivery verification (V2 graph + frontend + E2E).

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

## V1 and V2 Relationship

- V1 remains default (`AGENT_RUNTIME_BACKEND=v1`).
- V2 is opt-in (`AGENT_RUNTIME_BACKEND=v2`) and depends on `langgraph`.
- Session business truth remains `SessionContext` in session storage.
- V2 adds graph orchestration, checkpoint, runtime events, and review workflow on top.

## UI Surfaces

- Streamlit (`python main.py run-ui`): existing UI, kept for compatibility/demo continuity
- React frontend (`frontend/`):
  - Discussion Console (`/sessions`, `/sessions/:sessionId`)
  - Runtime Review Console (`/runtime-reviews`, `/runtime-reviews/:reviewId`)

## Quick Start (Demo Path)

1. `python -m pip install -e ".[dev,graph]"`
2. `python main.py bootstrap-dev-snapshot`
3. `python main.py run-api --host 127.0.0.1 --port 8000`
4. New terminal:
   - `cd frontend`
   - `npm install`
   - `npm run codegen:openapi`
   - `npm run dev`
5. Open frontend and run:
   - create session
   - submit user turn
   - run next turn
   - open runtime reviews if interrupt occurs
   - inspect transcript + runtime timeline

## Testing and Quality Guardrails

- Python baseline: `pytest -m "not v2_graph" -q`
- Python full: `pytest -q`
- Frontend guard: `cd frontend && npm run quality:guard`
- Playwright mock: `cd frontend && npm run e2e:mock`
- Playwright real backend: `cd frontend && npm run e2e:real`

## Documentation Index

- `docs/test_matrix.md` - official minimal/full test matrix
- `docs/local_runbook.md` - local run/install/run/test instructions
- `docs/final_handover_runbook.md` - final demo/handover steps
- `docs/agent_runtime_v2.md` - V2 architecture and boundaries
- `docs/review_workflow_v2.md` - review workflow details
- `docs/runtime_timeline_v2.md` - transcript/timeline API contract
- `docs/frontend_discussion_console.md` - discussion frontend notes
- `docs/frontend_runtime_review_console.md` - review frontend notes
- `docs/frontend_codegen_and_e2e.md` - codegen + Playwright usage
- `docs/release_scope_and_freeze.md` - scope freeze and backlog boundary
- `KNOWN_LIMITATIONS_FINAL.md` - known limits and non-goals

## Known Limitations (Short)

- Review queue is file-backed and single-node oriented (not distributed-consensus storage).
- Verifier remains heuristic-first by default.
- Timeline UI is list-oriented (not a DAG visual graph).
- Some frontend type migration remains in transition layer (`generated-adapters.ts`).
- Platform is not positioned as multi-tenant production SaaS.

See `KNOWN_LIMITATIONS_FINAL.md` for full details.
