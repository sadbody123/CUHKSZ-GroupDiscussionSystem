# Known Limitations and Non-Goals (Freeze)

This file lists known boundaries for the current delivery. These are not hidden bugs;
they are explicit scope limits at freeze time.

## Runtime / Backend

- V2 runtime depends on `langgraph`; minimal mode intentionally does not require it.
- Review queue storage is file-backed (`storage/agent_runtime_v2/review_queue`) and designed for single-node/local workflow.
- Checkpoint/events are file-based observability assets, not distributed transaction logs.
- V1 remains default runtime backend; V2 is opt-in.

## Quality / Review

- Quality verifier is heuristic-first by default.
- LLM-assisted verifier is not part of current frozen delivery.
- Review workflow is operational for local/API usage, but not hardened for multi-instance consensus.

## Frontend / E2E

- Timeline panel is list-centric and does not provide advanced graph visualization.
- Frontend types use generated OpenAPI types via adapter layer; a small hand-written transition surface may still exist.
- Real-backend Playwright currently emphasizes discussion path; review real-backend deep coverage remains limited.

## Platform / Product Boundaries

- This project is not positioned as production SaaS:
  - no full auth/multi-tenant hardening
  - no distributed consistency guarantees
  - no production SLAs
- Advisory analytics (speech/learner/review calibration) must not be interpreted as official grading/certification.

## Out of Scope For This Release

- Replacing review queue with database-backed strong-consistency design.
- Full DAG-style runtime trace visualization UI.
- Full provider matrix expansion beyond current adapter-backed path.
