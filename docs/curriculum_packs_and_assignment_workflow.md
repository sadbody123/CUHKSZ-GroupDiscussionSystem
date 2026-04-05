# Curriculum packs and assignment workflow

Phase 15 adds **training delivery** scaffolding: curriculum YAML packs, local **assignments**, step-level **attempts**, and **delivery reports**. This is **not** an LMS, gradebook, or official homework system.

## Typical flow

1. Choose a **curriculum pack** (builtin YAML under `app/curriculum/packs/` or custom JSON in `storage/curriculum_packs/custom/`).
2. Create an **assignment** for one or more local `learner_id` values.
3. **Launch** a pack step → creates a normal discussion **session** tagged with `curriculum_pack_id`, `assignment_id`, `assignment_step_id`.
4. Run turns and feedback as usual; optionally **attach** the session to the step for completion tracking.
5. Generate an **assignment report** (JSON; training analytics only).

## CLI / API

See `list-curriculum-packs`, `create-assignment`, `launch-assignment-step`, `attach-session-to-assignment-step`, `generate-assignment-report`, and FastAPI routes under `/curriculum-packs` and `/assignments`.
