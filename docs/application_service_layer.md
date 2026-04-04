# Application service layer (phase 5)

## Why it exists

The **application** package (`app/application/`) sits **above** `app/runtime/` and **below** HTTP/UI:

- **Runtime** owns snapshot loading, repositories, retrieval, orchestration, LLM providers, sessions on disk, and execution.
- **API** (`app/api/`) and **Streamlit** (`app/ui/`) should not re-implement business rules.

Services **compose** runtime primitives:

| Service | Responsibility |
|---------|----------------|
| `SnapshotService` | List/resolve local snapshot directories; summarize manifest/build report |
| `TopicService` | Topic cards from a snapshot (list/search/detail) |
| `SessionService` | Create/load/list/export `SessionContext` via `SessionManager` + `FileSessionStore` |
| `DiscussionService` | `TurnExecutor`, `auto_run_discussion`, session status |
| `FeedbackService` | Analyzer + `run_generate_feedback` / transcript-only analysis |

## Relationship to runtime

- Services call **`load_snapshot`**, **`TurnExecutor`**, **`SessionManager`**, **`run_generate_feedback`**, etc.
- No duplicate state machine or router logic; parameters are validated at the application/API boundary.

## API and UI

- FastAPI routers depend on services through **`app/api/deps.py`**.
- Streamlit uses **`DiscussionApiClient`** → HTTP → same FastAPI → same services (default path).

This keeps a single place for “create session / run turn / feedback” behavior.
