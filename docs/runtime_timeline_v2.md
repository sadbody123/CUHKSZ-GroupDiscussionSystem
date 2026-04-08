## Runtime Timeline V2 API

### Purpose

Expose existing V2 runtime event logs to frontend tools without introducing a new tracing subsystem.

The timeline API reads from:

- `${AGENT_RUNTIME_V2_DIR}/events/runtime_v2_events.jsonl`

### Endpoints

- `GET /sessions/{session_id}/runtime-events`
  - query params:
    - `offset` (default `0`)
    - `limit` (default `50`, max `200`)
    - `run_id` (optional)

- `GET /sessions/{session_id}/transcript`
  - query params:
    - `offset` (default `0`)
    - `limit` (default `50`, max `200`)

### Runtime event fields

Each event item exposes the normalized fields currently written by `RuntimeEventLogger`:

- `timestamp`
- `run_id`
- `session_id`
- `backend`
- `node_name`
- `next_actor`
- `stop_reason`
- `success`
- `error_summary`
- `trace_id`
- `checkpoint_id`
- `quality_decision`
- `interrupt_reason`
- `repair_count`
- `quality_flags`
- `review_id`
- `policy_id`

### Transcript fields

Transcript pagination API returns:

- `turn_id`
- `sequence`
- `speaker_role`
- `text`
- `created_at`
- `manual_override`
- `review_id`
- `run_id`
- `metadata`

### Notes

- `GET /sessions/{session_id}` remains unchanged and still includes `latest_turns`.
- `transcript` API is the preferred source for full-scroll transcript UI.
- timeline API is read-only and intentionally mirrors current JSONL trace shape.
- timeline/event storage is local file-backed and intended for single-node workflow.
