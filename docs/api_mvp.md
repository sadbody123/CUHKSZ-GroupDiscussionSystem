# FastAPI MVP (phase 5)

## Architecture

- **`app/api/main.py`** — `create_app()`, request-id middleware, CORS, error handlers, included routers.
- **`app/api/routers/`** — `health`, `snapshots`, `topics`, `sessions`, `feedback` (analyze-only).
- **`app/api/schemas/`** — Pydantic request/response models.
- **`app/api/deps.py`** — injects `AppConfig` and application services.
- **`app/api/error_handlers.py`** — maps `app.application.exceptions` to HTTP status codes.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Status, version, default provider, snapshot root, `app_env`, `app_version`, `default_runtime_profile`, optional `request_id` |
| GET | `/system/info` | Public app/env summary (paths, provider defaults, feature flags; no secrets) |
| GET | `/snapshots` | List local snapshots |
| GET | `/snapshots/{snapshot_id}` | Manifest/build summary + counts |
| GET | `/snapshots/{snapshot_id}/index-status` | Whether indexes exist, embedder, modes, item counts |
| GET | `/topics` | `snapshot_id` (query), optional `keyword` |
| GET | `/topics/{topic_id}` | `snapshot_id` (query) required |
| GET | `/sessions` | List sessions (file store) |
| POST | `/sessions` | Create session |
| GET | `/sessions/{session_id}` | Status + transcript + coach preview |
| POST | `/sessions/{session_id}/turns/user` | User message |
| POST | `/sessions/{session_id}/run-next` | One agent turn |
| POST | `/sessions/{session_id}/auto-run` | `max_steps` in body |
| POST | `/sessions/{session_id}/feedback` | Coach report + packet summary |
| GET | `/sessions/{session_id}/export` | Full session JSON |
| GET | `/feedback/sessions/{session_id}/analyze` | FeedbackPacket only (no coach text) |

## Example

```bash
curl -s http://127.0.0.1:8000/health
curl -s "http://127.0.0.1:8000/topics?snapshot_id=dev_snapshot_v2"
curl -s -X POST http://127.0.0.1:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"snapshot_id":"dev_snapshot_v2","topic_id":"<topic_from_list>","user_stance":"for","provider_name":"mock"}'
```

## Errors

| Status | Meaning |
|--------|---------|
| 400 | Invalid request |
| 404 | Unknown snapshot, topic, or session |
| 409 | Phase conflict (e.g. user turn in feedback phase) |
| 500 | Unexpected (details not exposed in production-minded deployments) |

See `app/application/exceptions.py` for codes.
