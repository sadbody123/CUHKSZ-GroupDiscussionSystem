# Runtime profiles (phase 6)

## Location

YAML files under `app/runtime/profiles/` (`default.yaml`, `balanced.yaml`, `concise.yaml`, `strict_coach.yaml`).

## Loading

- `app/runtime/profile_loader.py` — load a single YAML by id (filename stem).
- `app/runtime/profile_resolver.py` — merge any profile with **`default`** (deep merge for section dicts).

## Sections

| Section | Used for |
|---------|----------|
| `retrieval` | `top_k_by_role` overrides in `RoleRouter.build_context_packet` |
| `orchestration` | Phase thresholds in `SessionStateMachine` (`intro_turn_threshold`, `discussion_turn_threshold`, `summary_min_turns`) |
| `analyzer` | Thresholds / keyword lists passed to `analyze_transcript_turns` |
| `prompting` | `max_reply_chars_by_role` applied after mock/real generation in `run_agent_turn` |
| `coach` | Reserved / metadata for coach verbosity |

## Session binding

`sessions` store `runtime_profile_id` (default `default`). `TurnExecutor` and `run_agent_turn` resolve the merged profile on each use.

## CLI / API

- `python main.py list-profiles`, `show-profile --profile-id <id>`
- `GET /profiles`, `GET /profiles/{profile_id}`
