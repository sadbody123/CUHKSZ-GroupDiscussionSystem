## Frontend Discussion Console (Phase 8)

### What was added

The existing React/Vite frontend now includes a minimal **Discussion Console**:

- `GET /sessions` list and quick entry
- `POST /sessions` create session
- `GET /sessions/{session_id}` detail + transcript
- `GET /sessions/{session_id}/transcript` full transcript with offset/limit pagination
- `GET /sessions/{session_id}/runtime-events` runtime timeline events with offset/limit and optional `run_id`
- `POST /sessions/{session_id}/turns/user` submit user turn
- `POST /sessions/{session_id}/run-next` run single next turn
- `POST /sessions/{session_id}/auto-run` run multi-step discussion
- `POST /sessions/{session_id}/feedback` generate feedback

Routes:

- `/sessions`
- `/sessions/:sessionId`
- existing `/runtime-reviews*` routes remain unchanged

### Console linkage with Runtime Reviews

- Session detail page shows pending runtime reviews linked by `session_id`.
- Runtime review detail page provides a jump back to related session detail.
- Runtime timeline events containing `review_id` can jump to review detail.

### API and schema notes

This console is based on actual FastAPI routers/schemas:

- `app/api/routers/sessions.py`
- `app/api/schemas/session.py`
- `app/api/schemas/turn.py`
- `app/api/schemas/feedback.py`
- `app/api/schemas/session.py` (transcript/events DTOs)

Review list endpoint supports optional filters:

- `GET /runtime-reviews?status=...&session_id=...&topic_id=...`

### Type strategy

Current frontend still uses hand-written DTOs in `frontend/src/api/types.ts`, but type contract hardening was added:

1. discussion/session types are centralized in one place (no scattered component-local types)
2. OpenAPI codegen command is scaffolded:
   - `npm run codegen:openapi`
   - generates `frontend/src/api/generated/openapi.ts`

3. transition layer `frontend/src/api/generated-adapters.ts` isolates DTO imports for gradual migration to generated types.

This keeps current iteration fast while preparing migration to generated types.

### Run locally

1. Start backend:
   - `python main.py run-api --host 127.0.0.1 --port 8000`
2. Frontend:
   - copy `frontend/env.example` to `frontend/.env`
   - `cd frontend`
   - `npm install`
   - `npm run codegen:openapi` (recommended before build/test)
   - `npm run dev`

### Current limitations

- Session list has no server-side pagination yet.
- Timeline is list-based and not yet grouped by run/node categories.
- OpenAPI types are not yet fully wired into all pages.

### E2E

Playwright smoke coverage is available in:

- mock mode:
  - `frontend/e2e/discussion.spec.ts`
  - `frontend/e2e/review.spec.ts`
- real-backend mode:
  - `frontend/e2e-real/discussion.real.spec.ts`
