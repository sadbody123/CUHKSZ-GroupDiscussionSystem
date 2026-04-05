# Micro-drill engine

**Drill specs** live under `app/modes/drills/` as YAML (`DrillSpec`). The **drill generator** (`app/modes/engines/drill_generator.py`) ranks drills against a learner’s `weak_skills` and returns explainable recommendations (scores and reasons).

- `ModeService.generate_drills_for_learner` is exposed as `GET /learners/{learner_id}/drills` and the `generate-drills` CLI command.
- Drills do not replace the main discussion runtime; they attach metadata and constraints via `ModeService.on_user_turn_committed` and `SessionContext.mode_state`.
