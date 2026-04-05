"""Bridge learner learning plan to curriculum pack draft."""

from __future__ import annotations

from datetime import datetime, timezone

from app.curriculum.schemas.pack import CurriculumPack, CurriculumPackStep
from app.learner.schemas.plan import LearningPlan


def pack_from_learning_plan(
    plan: LearningPlan,
    *,
    pack_id: str,
    display_name: str,
) -> CurriculumPack:
    """Deterministic pack draft from plan steps."""
    now = datetime.now(timezone.utc).isoformat()
    steps: list[CurriculumPackStep] = []
    for i, row in enumerate(plan.steps or [], start=1):
        if not isinstance(row, dict):
            continue
        steps.append(
            CurriculumPackStep(
                step_id=str(row.get("step_id") or f"plan_step_{i}"),
                order=int(row.get("order") or i),
                title=str(row.get("title") or f"Step {i}"),
                objective=str(row.get("objective") or ""),
                step_type="topic_practice",
                topic_id=row.get("topic_id"),
                mode_id=row.get("mode") or row.get("mode_id"),
                runtime_profile_id=row.get("runtime_profile_id"),
                focus_skills=list(row.get("focus_skills") or []),
                metadata={"reason": "from_learning_plan", "plan_id": plan.plan_id},
            )
        )
    return CurriculumPack(
        pack_id=pack_id,
        display_name=display_name,
        description="Draft generated from learning plan (training delivery).",
        author_id=plan.learner_id,
        created_at=now,
        target_skills=[],
        steps=steps,
        metadata={"source": "planning_bridge", "learner_id": plan.learner_id},
    )
