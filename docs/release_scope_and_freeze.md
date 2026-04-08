# Release Scope and Freeze (Current Delivery)

## Delivery Scope Included

- Backend:
  - FastAPI API + application service layer
  - V1 runtime (default) and V2 runtime (LangGraph, opt-in)
  - quality/repair/interrupt/review workflow
  - transcript pagination API
  - runtime events/timeline API
- Frontend:
  - Discussion Console
  - Runtime Review Console
  - OpenAPI codegen pipeline
  - Playwright mock and real-backend E2E modes
- Engineering:
  - minimal/full dependency strategy
  - pytest marker strategy (`v2_graph`)
  - CI matrix: `baseline` and `full-v2-fullstack`

## Stable vs Optional

### Stable / Recommended

- V1 default path
- Session discussion flow with mock provider
- Runtime review operations and linkage in frontend
- Transcript/timeline read APIs
- Baseline and full test matrix commands

### Optional / Conditional

- V2 runtime path (`AGENT_RUNTIME_BACKEND=v2`)
- LangGraph-dependent tests and behaviors
- Real-backend Playwright mode
- Cloud provider integrations (non-mock)

## Explicit Non-Goals For This Freeze

- No production-grade multi-tenant/auth hardening
- No database migration for review queue/checkpoint/event storage
- No full DAG visualization UI for timeline
- No LLM-assisted verifier as default policy

## Post-Freeze Backlog (Not Part Of This Delivery)

- Expand real-backend E2E to include stable review mutation path
- Complete migration from residual hand-written frontend types to generated contract only
- Introduce optional stronger storage backend for review queue/checkpoints
- Add richer runtime timeline visual analytics

## Version Note

Project version remains `0.1.0` (no version bump in this freeze round).
