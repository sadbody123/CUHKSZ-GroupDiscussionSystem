# Observability & logging (phase 7)

## Logging

- `setup_logging()` (`app/logging.py`) configures the root logger via `app/ops/logging_config.py`.
- **Plain text** (default): lines include `request_id` and `session_id` placeholders from trace context.
- **Structured** (`STRUCTURED_LOGGING=true`): JSON lines with `request_id`, `session_id`, `eval_run_id`, `trace_id`, `message`, `logger`, `level`.

## Trace context (`app/ops/trace.py`)

`contextvars` hold:

- `request_id` — HTTP request or synthetic CLI/eval id.
- `session_id` — discussion session (when set by callers).
- `eval_run_id` — evaluation run identifier.
- `trace_id` — optional correlation id.

Helpers: `set_*`, `get_*`, `reset_*`, `trace_extra()`.

## HTTP `X-Request-ID`

`RequestContextMiddleware` (`app/api/middleware/request_context.py`):

- Accepts incoming `X-Request-ID` or generates a UUID.
- Sets `request.state.request_id` and trace context for the request.
- Echoes `X-Request-ID` on every response.

Error JSON bodies from `register_error_handlers` may include `request_id` when the context is set.

## API health

`GET /health` returns `request_id` when available and non-secret summary fields (`app_env`, `app_version`, `default_runtime_profile`).

`GET /system/info` returns public configuration summary (paths, provider defaults, feature flags). Secrets (e.g. API keys) are never included.
