## Runtime Review Workflow V2

### Scope

This document describes the lightweight review workflow used by runtime V2 quality interruptions.

It is separate from the legacy review workspace (`/reviews`) and focuses on:

- quality interrupt handoff,
- editable draft review,
- controlled resume.

### Data model

Review items are stored at:

- `${AGENT_RUNTIME_V2_DIR}/review_queue/*.json`

Core fields:

- identifiers: `review_id`, `session_id`, `run_id`, `checkpoint_id`
- quality context: `reason`, `interrupt_reason`, `quality_flags`
- editable content: `draft_reply_text`, `draft_reply_summary`
- state/control: `status`, `version`, `allowed_actions`
- audit: `review_decision_payload`, `resolved_by`, `updated_by`, `notes`, timestamps

### Status machine

Allowed transitions:

- `pending -> approved | rejected | resumed | resolved`
- `approved -> resumed | resolved`
- `rejected -> resolved`
- `resumed -> resolved`

Optimistic concurrency:

- every review item has `version`
- mutating operations can require `expected_version`
- mismatched version raises conflict error

### Edited draft path

`apply_edited_draft` runs through controlled steps:

1. validate review state and version
2. update review item with edited draft
3. append manual override turn to session through runtime facade
4. record decision payload and audit metadata
5. optional resume from review

No direct session file mutation is done by review store or API callers.

### Service and API

Application service:

- `app/application/runtime_review_service.py`

API endpoints:

- `GET /runtime-reviews`
- `GET /runtime-reviews/{review_id}`
- `POST /runtime-reviews/{review_id}/approve`
- `POST /runtime-reviews/{review_id}/reject`
- `POST /runtime-reviews/{review_id}/resume`
- `POST /runtime-reviews/{review_id}/apply-edited-draft`
- `GET /runtime-reviews/metrics/summary`

### Current limitations

- metrics are aggregate-only and file-backed
- no distributed locking (single-node local workflow)
- LLM-assisted verifier remains an extension point, not default behavior

### Freeze status

Stable in this delivery:

- pending/approve/reject/resume/apply-edited-draft flow
- optimistic concurrency (`expected_version`)
- session/detail linkage with frontend consoles

Post-freeze enhancements (not included now):

- stronger backend storage model for multi-instance consistency
- richer review analytics and audit dashboards
- deeper real-backend E2E coverage for full review mutation paths
