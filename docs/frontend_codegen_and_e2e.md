## Frontend Codegen and E2E Guardrails (Phase 10)

### OpenAPI codegen flow

From `frontend/`:

1. `npm run codegen:openapi:export`
   - runs `python scripts/export_openapi.py`
   - exports backend OpenAPI schema to:
     - `frontend/src/api/generated/openapi.schema.json`
2. `npm run codegen:openapi`
   - exports schema
   - generates:
     - `frontend/src/api/generated/openapi.ts`

### Why this replaced direct localhost fetching

Previous script depended on `http://localhost:8000/openapi.json`.  
That can pass/fail depending on whether backend is already running.

Current script exports schema directly from backend app code (`create_app().openapi()`),
so generation is deterministic and does not require manually starting API server first.

### Generated type usage strategy

- Generated file: `frontend/src/api/generated/openapi.ts`
- Adapter layer: `frontend/src/api/generated-adapters.ts`

API modules and hooks should import DTOs from `generated-adapters.ts`, not from
`generated/openapi.ts` directly. This keeps migration changes isolated.

Phase 10 key coverage in adapter:

- runtime reviews DTOs
- sessions DTOs
- transcript DTOs
- runtime events DTOs
- discussion action DTOs

### Playwright E2E

Installed as dev dependency:

- `@playwright/test`

Commands from `frontend/`:

- install browser: `npm run e2e:install`
- run mock-route tests: `npm run e2e:mock`
- run real-backend tests: `npm run e2e:real`
- default alias: `npm run e2e` (mock mode)

Current E2E specs:

- `frontend/e2e/discussion.spec.ts`
  - `/sessions` create -> detail -> submit user turn -> run next turn -> transcript update
- `frontend/e2e/review.spec.ts`
  - `/runtime-reviews` list -> detail -> edit draft -> apply edited draft
- `frontend/e2e-real/discussion.real.spec.ts`
  - real backend mode: create session -> submit user turn -> run next turn -> transcript shows input

### Mock vs real-backend modes

- `mock` mode (`e2e:mock`) is stable and deterministic, using route interception.
- `real` mode (`e2e:real`) runs against local FastAPI backend + frontend dev server and validates integration path.
  - backend startup script: `frontend/scripts/run_real_backend_e2e.py`
  - this script bootstraps `dev_snapshot_v2` before serving API.
- Use mock mode for frequent local/CI smoke; use real mode for higher-confidence integration checks.

### Local quality guard

From `frontend/`:

- `npm run quality:guard`
  - `codegen:openapi`
  - `test`
  - `build`

### CI integration

`.github/workflows/ci.yml` includes `frontend-quality` job that runs:

1. `npm install`
2. `npm run quality:guard`
3. `npx playwright install --with-deps chromium`
4. `npm run e2e`

### Troubleshooting

If `codegen:openapi` fails:

1. verify Python environment can import backend package:
   - `python -c "from app.api.main import create_app; print(create_app().title)"`
2. verify output folder is writable:
   - `frontend/src/api/generated/`
3. rerun export only:
   - `npm run codegen:openapi:export`
4. if `openapi.ts` generation fails:
   - delete stale output and rerun `npm run codegen:openapi`
