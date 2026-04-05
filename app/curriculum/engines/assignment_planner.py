"""Build AssignmentSpec from CurriculumPack."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.curriculum.constants import AS_ACTIVE, AS_DRAFT
from app.curriculum.schemas.assignment import AssignmentSpec, AssignmentStepRef
from app.curriculum.schemas.pack import CurriculumPack


def plan_assignment_from_pack(
    pack: CurriculumPack,
    *,
    learner_ids: list[str],
    title: str,
    created_by: str | None,
    description: str | None = None,
    due_at: str | None = None,
    activate: bool = True,
) -> AssignmentSpec:
    now = datetime.now(timezone.utc).isoformat()
    step_refs: list[AssignmentStepRef] = []
    for st in sorted(pack.steps, key=lambda x: x.order):
        step_refs.append(
            AssignmentStepRef(
                assignment_step_id=str(uuid.uuid4()),
                pack_step_id=st.step_id,
                learner_id=learner_ids[0] if len(learner_ids) == 1 else None,
                required=True,
                status="pending",
                metadata={"title": st.title},
            )
        )
    policy = {"min_completed_steps": 1, "mode": "training_delivery"}
    return AssignmentSpec(
        assignment_id=str(uuid.uuid4()),
        pack_id=pack.pack_id,
        learner_ids=list(learner_ids),
        created_at=now,
        created_by=created_by,
        title=title,
        description=description,
        due_at=due_at,
        status=AS_ACTIVE if activate else AS_DRAFT,
        total_steps=len(step_refs),
        completion_policy=policy,
        step_refs=step_refs,
        metadata={"planned_at": now},
    )
