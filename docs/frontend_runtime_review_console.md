## Frontend Runtime Review Console

### Why this frontend exists

This repository already has:

- FastAPI backend APIs,
- Streamlit UI (`app/ui`),
- V1/V2 runtime backends.

This frontend adds a dedicated TypeScript review console for V2 runtime review workflow,
without replacing Streamlit.

### Tech stack

- Vite
- React + TypeScript
- React Router
- TanStack Query
- Vitest + Testing Library

### Project location

- `frontend/`

### Local setup

1. Start backend (example):
   - `python main.py run-api --host 127.0.0.1 --port 8000`
2. Frontend env:
   - copy `frontend/env.example` to `frontend/.env`
   - set `VITE_API_BASE_URL` (default `http://localhost:8000`)
3. Install and run:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

### Build and tests

- `npm run build`
- `npm run test`
- `npm run codegen:openapi` (exports schema from backend code, then generates TS)
- `npm run e2e:mock` (Playwright mock-route)
- `npm run e2e:real` (Playwright real-backend integration)

### Runtime review features implemented

- Review list page (`/runtime-reviews`)
  - status filter
  - client-side session/topic quick filters
  - metrics cards
- Review detail page (`/runtime-reviews/:reviewId`)
  - runtime context, quality context, version display
  - draft editor
  - actions: approve/reject/resume/apply edited draft
  - expected_version passed for conflict protection
  - link back to related session detail (`/sessions/:sessionId`)
- Error/loading/empty state handling for core flows

### Backend APIs used

- `GET /runtime-reviews`
- `GET /runtime-reviews/{review_id}`
- `POST /runtime-reviews/{review_id}/approve`
- `POST /runtime-reviews/{review_id}/reject`
- `POST /runtime-reviews/{review_id}/resume`
- `POST /runtime-reviews/{review_id}/apply-edited-draft`
- `GET /runtime-reviews/metrics/summary`

### OpenAPI typing strategy

Review APIs are now wired through `src/api/generated-adapters.ts`, which maps to generated
OpenAPI types from `src/api/generated/openapi.ts`.

### Relation with Streamlit

Streamlit remains available and unchanged. This frontend is an additional UI surface
focused on V2 runtime review operations.
