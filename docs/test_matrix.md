## Test Matrix (Phase 11)

This project supports two explicit dependency/test modes.

### 1) Minimal / baseline mode (V1-first)

Use when you want fast validation without LangGraph:

```bash
python -m pip install -e ".[dev]"
python -m pytest -m "not v2_graph" -q
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
```

Characteristics:

- LangGraph is not required.
- V2 graph-specific tests are skipped/excluded through the `v2_graph` marker.
- V1/default behavior remains validated.

### 2) Full V2 / fullstack mode

Use when validating complete V2 runtime + frontend + E2E:

```bash
python -m pip install -e ".[dev,graph]"
python -m pytest -q
```

Frontend (from `frontend/`):

```bash
npm install
npm run codegen:openapi
npm run test
npm run build
npm run e2e:mock
npm run e2e:real
```

Characteristics:

- LangGraph is installed and V2 graph tests run normally.
- Includes frontend contract generation, unit/component tests, and Playwright.

### Marker policy

- `v2_graph`: tests that require LangGraph-backed V2 runtime.
- In environments without `langgraph`, `v2_graph` tests are auto-skipped by pytest collection logic.

### CI mapping

- `baseline` job -> minimal mode.
- `full-v2-fullstack` job -> full mode.

### Playwright mode split

- `e2e:mock`: stable route-intercept mode for fast regressions.
- `e2e:real`: real backend + frontend integration mode for higher-confidence checks.

### Platform note

Some shells (notably older PowerShell variants) do not support `&&`.
If needed, run commands one by one or use `;` separators.
