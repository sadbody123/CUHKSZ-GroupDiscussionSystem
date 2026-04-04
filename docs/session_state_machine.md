# Session state machine

## Phases (`SessionPhase`)

`prepare` → `intro` → `discussion` → `summary` → `feedback` → `ended`

## Transition rules (`SessionStateMachine.advance_phase`)

- `prepare` → `intro` if `topic_id` is set.
- `intro` → `discussion` when transcript has at least `INTRO_MIN_TURNS` (default 1).
- `discussion` → `summary` when turn count ≥ `DISCUSSION_MAX_TURNS` (default 12).
- `summary` → `feedback` when turn count ≥ `DISCUSSION_MAX_TURNS + SUMMARY_MIN_TURNS`.
- `feedback` → `ended` on next advance.

Thresholds live in `app/runtime/orchestrator/policies.py`.

## Next role (`suggest_next_role`)

Deterministic heuristics (no NLG):

- `prepare` → `user`
- `intro` → alternates `user` / `moderator`
- `discussion` → after `user`, pick `ally` or `opponent` using `hash(session_id) % 2`; after ally/opponent → `user`
- `summary` → `moderator` then `user`
- `feedback` → `coach`

## `TurnPlan`

`plan-turn` CLI uses `build_turn_plan` to return `next_role`, updated phase, and a `context_packet` dict from `RoleRouter` (no natural language reply).
