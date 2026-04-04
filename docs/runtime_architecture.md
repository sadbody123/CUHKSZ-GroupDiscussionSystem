# Runtime architecture (phases 3–4)

## Scope

Runtime **only consumes** offline snapshots under `app/knowledge/snapshots/<id>/`. It does **not** read Datahub exports, upstream SQLite, or the network.

## Components

| Module | Role |
|--------|------|
| `snapshot_loader.py` | Load `manifest.json`, `build_report.json`, JSONL tables into `SnapshotBundle` |
| `repositories/` | Thin read-only indexes over pedagogy / topic / evidence_index / normalized docs / source catalog |
| `retrieval/` | Rule-based filters, ranking, `RoleRouter` assembling `RoleContextPacket` |
| `orchestrator/` | Deterministic `SessionStateMachine` → `TurnPlan` + embedded context dict |
| `evaluation/` | Transcript metrics, rule signals, `FeedbackPacket` assembly |
| `prompt_loader.py` + `prompts/*.md` | Template ids and markdown for role prompts |
| `session/store.py` | In-memory / JSON helpers (legacy / demos) |
| `llm/` | Provider abstraction: **mock** (default) and optional OpenAI-compatible HTTP |
| `render/` | Placeholder-based prompt rendering from `RoleContextPacket` + transcript window |
| `agents/` | Per-role agents calling renderer + provider → `AgentReply` / `CoachReport` |
| `session/` (`file_store.py`, `manager.py`) | File-backed sessions under `storage/sessions/` |
| `execution/` | Turn executor, discussion loop, feedback runner |

## LLM and defaults

Phase 4 adds **optional** text generation. The **mock** provider is deterministic and requires no API key. Structured payloads from phase 3 (`RoleContextPacket`, `TurnPlan`, `FeedbackPacket`) are still the source of truth; the LLM layer renders and executes on top of them.

See [LLM integration](llm_integration.md) and [CLI discussion MVP](cli_discussion_mvp.md).

## Phase 5 wrappers

HTTP and UI are implemented in **`app/application/`**, **`app/api/`**, and **`app/ui/`** and call the same runtime primitives as the CLI. See [application_service_layer.md](application_service_layer.md) and [api_mvp.md](api_mvp.md).
