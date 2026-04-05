# Phase 7 — Engineering hardening & delivery

This phase adds **configuration**, **environment checks**, **artifact tracking**, **snapshot bundles**, **structured logging / trace context**, **API request IDs**, **Docker/Compose**, and **CI** — without changing the frozen runtime boundaries (offline snapshot, read-only runtime, mock-first).

## How the pieces fit

| Component | Role |
|-----------|------|
| `app/ops/settings.py` | Single `UnifiedSettings` (`.env` + env vars) for paths, provider defaults, API/UI ports. |
| `app/ops/env_validator.py` | Structured `validate_environment()` for CLI/CI. |
| `app/ops/artifacts/` | Passive filesystem scan — snapshots, session JSON exports, eval/feedback reports, bundle zips. |
| `app/ops/bundles/` | Export/import snapshot directories as signed zip bundles (`bundle_manifest.json` + `checksums.sha256`). |
| `app/ops/logging_config.py` + `trace.py` | Optional JSON-ish logs; `request_id` / `session_id` / `eval_run_id` via `contextvars`. |
| `app/api/middleware/request_context.py` | Injects `X-Request-ID` and logging context per HTTP request. |
| `docker/` + `Makefile` + `scripts/` | Local run and container templates (not production-tuned). |
| `.github/workflows/ci.yml` | `pytest`, `validate-env`, `run-smoke`, minimal `run-evals` on mock. |

`app/config.py` and `app/application/config.py` read path and numeric defaults from `get_ops_settings()` so offline build and API stay aligned.
