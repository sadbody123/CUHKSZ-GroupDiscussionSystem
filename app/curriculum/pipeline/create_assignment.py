"""Create assignment from pack."""

from __future__ import annotations

from app.curriculum.engines.assignment_planner import plan_assignment_from_pack
from app.curriculum.schemas.pack import CurriculumPack
from app.curriculum.store.assignment_store import AssignmentStore


def run_create_assignment(
    pack: CurriculumPack,
    store: AssignmentStore,
    *,
    learner_ids: list[str],
    title: str,
    created_by: str | None,
    description: str | None = None,
    due_at: str | None = None,
) -> object:
    spec = plan_assignment_from_pack(
        pack,
        learner_ids=learner_ids,
        title=title,
        created_by=created_by,
        description=description,
        due_at=due_at,
        activate=True,
    )
    store.create_assignment(spec)
    return spec
