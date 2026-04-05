"""Map LearningPlanStep dict to SessionLaunchSpec."""

from __future__ import annotations

from typing import Any

from app.modes.planning.session_launch_spec import SessionLaunchSpec


def step_to_launch_spec(step: dict[str, Any], *, snapshot_id: str, learner_id: str | None) -> SessionLaunchSpec:
    practice_mode = step.get("practice_mode_id") or (
        "micro_drill" if step.get("focus_skills") else "free_practice"
    )
    preset = step.get("preset_id") or ("micro_drill" if practice_mode == "micro_drill" else "free_practice")
    return SessionLaunchSpec(
        snapshot_id=snapshot_id,
        topic_id=str(step.get("topic_id") or ""),
        mode_id=practice_mode,
        preset_id=preset,
        drill_id=step.get("drill_id"),
        assessment_template_id=step.get("assessment_template_id"),
        runtime_profile_id=step.get("runtime_profile_id"),
        audio_enabled=str(step.get("mode") or "").lower() in ("audio", "mixed"),
        focus_skills=list(step.get("focus_skills") or []),
        linked_pedagogy_item_ids=list(step.get("linked_pedagogy_item_ids") or []),
        learner_id=learner_id,
        metadata={"from_learning_plan": True, "step_order": step.get("order")},
    )
