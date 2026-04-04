# Prompt rendering (phase 4)

## Template sources

Markdown files under **`app/runtime/prompts/`**:

| File | Role |
|------|------|
| `moderator.md` | Facilitation / turn management |
| `ally.md` | Support user’s line of argument |
| `opponent.md` | Challenge and probe |
| `coach.md` | Formative feedback (feedback phase) |
| `user_support.md` | Optional user-facing help |

**`app/runtime/prompt_loader.py`** resolves template ids and loads raw text.

## Renderer

- **`app/runtime/render/prompt_renderer.py`** — `render_prompt_for_role(...) -> RenderedPrompt`.
- **`app/runtime/render/packet_serializer.py`** — short string summaries for topic card, pedagogy rows, evidence rows.
- **`app/runtime/render/transcript_window.py`** — formats recent `TranscriptTurn` lines for the prompt.

## Placeholders

The renderer supports simple **`{{NAME}}`** substitution with these keys:

- `TOPIC_CARD` — from `RoleContextPacket.topic_card`
- `PEDAGOGY` — from `pedagogy_items` in the packet
- `EVIDENCE` — from `evidence_items`
- `TRANSCRIPT_WINDOW` — from recent transcript turns
- `PHASE` — session phase string
- `USER_STANCE` — e.g. `for` / `against`
- `FEEDBACK_PACKET` — JSON or text for coach (feedback phase)
- `ROLE` — logical role name

If a template file contains **no** `{{...}}` placeholders, the static instructions from the file are **prepended** to a **default structured block** that still injects topic, pedagogy, evidence, and transcript. That keeps older short templates useful without dropping context.

## Schema

**`RenderedPrompt`** (`app/runtime/schemas/agent.py`): `role`, `template_id`, optional `system_prompt`, `user_prompt`, `metadata`.

No heavy template engine is required; behavior is stable and easy to test in **`tests/test_prompt_renderer.py`**.
