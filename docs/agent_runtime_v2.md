## Agent Runtime V2 (Phase 6)

### Release freeze snapshot

This document reflects the current delivery state, not a future roadmap draft.

Stable/available now:

- V2 discussion graph execution (opt-in backend)
- quality -> repair -> interrupt branch
- review queue and edited draft workflow
- checkpoint/event logging and session-level transcript/timeline APIs

Optional/conditional:

- V2 path requires `langgraph` dependency
- cloud provider behavior beyond mock path depends on environment

Post-freeze enhancements are tracked separately in `docs/release_scope_and_freeze.md`.

### Why introduce V2

The current runtime is production-usable and centered on `DiscussionService + TurnExecutor`.
V2 introduces a graph-native runtime track to prepare for:

- explicit node/state orchestration,
- multi-provider model support beyond OpenAI-compatible APIs,
- future LangGraph integration without forcing V1 migration in one step.

V2 still does **not** replace V1. It remains an opt-in backend.

### V1/V2 coexistence and switching

- New setting: `AGENT_RUNTIME_BACKEND` (`v1` or `v2`), default `v1`.
- New storage root: `AGENT_RUNTIME_V2_DIR` (default `storage/agent_runtime_v2`).
- Default is `v1` to preserve existing behavior.
- `DiscussionService` now checks this config:
  - `v1`: existing `TurnExecutor` path.
  - `v2`: route to `AgentRuntimeFacade` in `app/agent_runtime_v2/`.

No API/CLI contract changes are required in this phase.

### LangGraph dependency policy

V2 graph runtime depends on `langgraph`, but project install/test modes are now explicit:

- **minimal / baseline mode**: `pip install -e ".[dev]"` (no LangGraph required)
- **full V2 mode**: `pip install -e ".[dev,graph]"` (LangGraph installed)

Pytest marker policy:

- tests requiring LangGraph are marked `v2_graph`
- when `langgraph` is missing, `v2_graph` tests are auto-skipped
- baseline command: `pytest -m "not v2_graph" -q`
- full command: `pytest -q`

### V2 provider abstraction

`app/agent_runtime_v2/providers/` defines vendor-neutral interfaces:

- `ChatProvider`
- `EmbeddingProvider`
- `ModelCapabilities`
- request/response models (`ChatRequest`, `ChatResponse`, `EmbeddingRequest`, `EmbeddingResponse`)

Adapters currently implemented:

- `MockChatProvider` (wraps V1 `MockProvider`)
- `OpenAICompatibleChatProvider` (wraps V1 `OpenAICompatibleProvider`)

Embedding is currently interface-first only; adapter implementation is left as TODO.

### GraphState vs SessionContext boundaries

- `SessionContext` remains the persisted business source of truth (turns, phase, metadata).
- `DiscussionGraphState` stores runtime control data only:
  `session_id`, `runtime_profile_id`, `phase`, `last_role`, `next_actor`,
  `stop_reason`, `loop_index`, `max_steps`, plus optional trace metadata.

V2 does not create a second authoritative transcript store.

### Unified compiled graph runtime

`app/agent_runtime_v2/graphs/discussion_graph.py` builds one shared LangGraph `StateGraph`.
Both API paths call the same facade runtime entry:

- `run_next_turn(session_id)` -> `run(session_id, max_steps=1)`
- `auto_run_discussion(session_id, max_steps=n)` -> `run(session_id, max_steps=n)`

Graph node flow:

1. `load_session`
2. `select_next_actor`
3. `generate_turn`
4. `quality_check`
5. `repair_turn` (conditional)
6. `interrupt_for_review` (conditional)
7. `persist_session`
8. `stop_check`

Current `generate_turn` still bridges to V1 `TurnExecutor` for generation internals.
Loop control, stop policy, checkpoints, and tracing are handled by V2 graph runtime.

Routing:

- If `next_actor` resolves to user or a stop reason exists, graph goes to `stop_check`.
- Otherwise it runs `generate_turn -> quality_check`.
- `quality_check` routes to `persist_session` / `repair_turn` / `interrupt_for_review`.
- `repair_turn` loops back to `quality_check` with `max_repairs` guard.
- `stop_check` loops back to `select_next_actor` until max steps or another stop reason.

### QualityPolicy and verifier extension

Phase-5 moves quality behavior from hardcoded node constants to a policy + verifier layer.

Policy object:

- `app/agent_runtime_v2/policy/quality_policy.py`
- `QualityPolicyResolver` loads policy from runtime profile metadata:
  - `metadata.quality_policy` in profile YAML
- supported fields:
  - `min_reply_length`
  - `topic_relevance_threshold`
  - `response_linkage_threshold`
  - `max_repairs`
  - `interrupt_after_max_repairs`
  - `enable_interrupt`
  - `per_role_overrides`

Current profile integration:

- `default` profile defines baseline quality policy and role override sample.
- `concise` profile demonstrates stricter repair/interruption behavior (`max_repairs=0`, interrupt disabled).

Verifier extension point:

- `app/agent_runtime_v2/verifier/base.py`:
  - `QualityVerifier`
  - `VerifierDecision`
- default implementation: `HeuristicQualityVerifier`

This makes it straightforward to insert an optional LLM-assisted verifier later:

1. heuristic pre-check
2. optional LLM verifier call
3. escalation policy (`pass/repair/interrupt`)

### Quality branch (policy-driven)

Phase-5 quality branch is policy-driven:

- `quality_check` decides: `pass` | `repair` | `interrupt`
- `repair_turn` performs a bounded deterministic rewrite (`max_repairs=1` by default)
- `interrupt_for_review` stops run with `stop_reason=interrupt_for_review`

Current quality checks are heuristic-first (no extra verifier LLM call):

- reply too short,
- weak topic relevance,
- weak linkage to previous turn.

### Review workflow (interrupt handoff)

When `interrupt_for_review` is triggered, V2 now creates a review item in a separate store.

Review components:

- schema: `app/agent_runtime_v2/review/schemas.py`
- store: `app/agent_runtime_v2/review/store.py`
- service: `app/agent_runtime_v2/review/service.py`
- storage: `${AGENT_RUNTIME_V2_DIR}/review_queue/*.json`

Review item fields include:

- `review_id`
- `session_id`
- `run_id`
- `checkpoint_id`
- `topic_id`
- `reason` / `interrupt_reason`
- `quality_flags`
- `draft_reply_summary`
- `status` (`pending/approved/rejected/resumed/resolved`)
- `created_at` / `updated_at`

Facade-level integration points (future API-friendly):

- `list_pending_reviews()`
- `get_review(review_id)`
- `approve_review(review_id, action=...)`
- `resume_from_review(review_id, additional_steps=...)`

### Application/API integration (phase 6)

Runtime review workflow is now promoted to application and API surfaces:

- application service: `app/application/runtime_review_service.py`
- API router: `app/api/routers/runtime_reviews.py`
- API DTOs: `app/api/schemas/runtime_review.py`

API endpoints:

- `GET /runtime-reviews?status=pending`
- `GET /runtime-reviews/{review_id}`
- `POST /runtime-reviews/{review_id}/approve`
- `POST /runtime-reviews/{review_id}/reject`
- `POST /runtime-reviews/{review_id}/resume`
- `POST /runtime-reviews/{review_id}/apply-edited-draft`
- `GET /runtime-reviews/metrics/summary`

These endpoints are intentionally scoped to V2 runtime review items and do not replace
the existing review workspace APIs under `/reviews`.

### Editable draft path (manual override)

`apply_edited_draft` now provides an explicit controlled path:

1. validate review status/version in review service
2. store edited draft on review item
3. append a controlled manual-override turn to `SessionContext` via service/facade (not direct file edits)
4. update review status and audit payload
5. optionally resume graph execution

### Checkpoint strategy

Checkpoint implementation is a small file-backed store:

- `app/agent_runtime_v2/store/checkpoint_store.py`
- location: `${AGENT_RUNTIME_V2_DIR}/checkpoints/*.json`
- data: latest graph control state (`run_id`, loop counters, stop reason, status, trace metadata, emitted turn ids, policy snapshot id, review id, etc.)

Why this choice:

- keeps V2 checkpointing independent from `storage/sessions/`,
- easy to inspect/debug locally,
- sufficient for minimal resume semantics before introducing heavier infrastructure.

### Stop policy

V2 uses explicit stop reasons in graph state/checkpoints/events:

- `need_user_input`
- `max_steps_reached`
- `phase_complete`
- `error`
- `completed`
- `interrupt_for_review`

Run status derives from stop reason:

- `running`
- `interrupted` (for `need_user_input` / `max_steps_reached` / `interrupt_for_review`)
- `completed` (for `completed` / `phase_complete`)
- `failed` (for `error`)

### Resume semantics

`AgentRuntimeFacade.resume_run(session_id, run_id=None, additional_steps=1)`:

- loads checkpoint by `run_id` (or latest by `session_id`),
- validates that checkpoint-emitted turn ids still exist in `SessionContext` (minimal duplicate guard),
- extends run budget with `additional_steps`,
- re-invokes the same compiled graph loop.

Current constraints:

- resume is state-light and intended for simple continuation scenarios,
- it relies on persisted `SessionContext` and checkpoint control state,
- if checkpoint status is already `completed`, resume returns `completed_noop`,
- it does not yet implement branching/replay timelines.

### Draft / persist boundary

Current boundary in graph control flow:

- `generate_turn` creates in-memory draft turn content.
- `repair_turn` edits draft content in-memory.
- `persist_session` is the node that writes final turn to session store.

Interrupt path behavior:

- if interrupted before `persist_session`, draft turn is not persisted to session storage.
- review item stores a draft reply summary for manual decision/resume.
- when manual edited draft is applied, persistence happens through controlled service/facade path.

### Trace / event log

Runtime V2 writes structured JSONL events:

- file: `${AGENT_RUNTIME_V2_DIR}/events/runtime_v2_events.jsonl`
- each record includes:
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

Review lifecycle events are also logged:

- review item created
- review status changed
- edited draft applied
- review resume completed

This log is designed as a minimal debug/replay aid.

### Session-level timeline and transcript APIs

To support frontend operational tooling without changing session truth boundaries:

- `GET /sessions/{session_id}/transcript?offset=&limit=` provides paginated full transcript turns.
- `GET /sessions/{session_id}/runtime-events?offset=&limit=&run_id=` provides paginated V2 runtime timeline events.

`/sessions/{session_id}` is unchanged and still includes `latest_turns` for compatibility.

### Current status

Implemented:

- V2 package skeleton with clear module responsibilities.
- unified compiled LangGraph discussion execution for both `run_next_turn` and `auto_run_discussion`.
- quality-based branch path (`quality_check` / `repair_turn` / `interrupt_for_review`).
- policy-driven quality configuration from runtime profiles.
- review queue handoff workflow for interrupts.
- runtime review application service + API integration.
- editable draft apply path with optimistic concurrency checks.
- minimal checkpoint store and resume flow.
- explicit stop policy + run status semantics.
- structured event logging.
- V1/V2 backend switch with V1 default.
- Provider abstraction and basic adapters.
- tests for backend switch, graph compile path, checkpoint/resume basics.

Not yet implemented in V2:

- graph-native feedback generation,
- first-class embedding adapters,
- advanced checkpoint branching/replay.
- full multi-agent graph orchestration.
- LLM-assisted quality verifier (currently heuristic-first).
- API router exposure for review queue operations (service layer exists; API remains optional).
- richer metrics/analytics over runtime events (current metrics are minimal aggregates).
