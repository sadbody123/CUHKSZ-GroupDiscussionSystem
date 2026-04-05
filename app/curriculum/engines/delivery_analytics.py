"""Aggregate delivery metrics and assignment reports."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.curriculum.constants import AS_COMPLETED, AS_IN_PROGRESS, STEP_COMPLETED, TRAINING_DELIVERY_NOTE
from app.curriculum.schemas.assignment import AssignmentSpec
from app.curriculum.schemas.delivery import DeliverySummary
from app.curriculum.schemas.report import AssignmentReport


def build_delivery_summary(spec: AssignmentSpec) -> DeliverySummary:
    total = max(spec.total_steps, 1)
    done = sum(1 for s in spec.step_refs if s.status == STEP_COMPLETED)
    rate = done / total
    next_ids = [s.pack_step_id for s in spec.step_refs if s.status != STEP_COMPLETED]
    return DeliverySummary(
        delivery_id=str(uuid.uuid4()),
        assignment_id=spec.assignment_id,
        learner_id=spec.learner_ids[0] if len(spec.learner_ids) == 1 else None,
        completed_steps=done,
        total_steps=spec.total_steps,
        completion_rate=round(rate, 4),
        last_activity_at=datetime.now(timezone.utc).isoformat(),
        recommended_next_step_ids=next_ids[:3],
        metadata={"note": TRAINING_DELIVERY_NOTE},
    )


def build_assignment_report(spec: AssignmentSpec, pack_summary: dict[str, Any]) -> AssignmentReport:
    now = datetime.now(timezone.utc).isoformat()
    step_rows = [
        {
            "assignment_step_id": s.assignment_step_id,
            "pack_step_id": s.pack_step_id,
            "status": s.status,
            "latest_session_id": s.latest_session_id,
        }
        for s in spec.step_refs
    ]
    learners = [{"learner_id": lid} for lid in spec.learner_ids]
    actions: list[str] = []
    if any(s.status != STEP_COMPLETED for s in spec.step_refs):
        actions.append("Continue remaining steps in pack order.")
    return AssignmentReport(
        report_id=str(uuid.uuid4()),
        assignment_id=spec.assignment_id,
        generated_at=now,
        pack_summary=pack_summary,
        learner_summaries=learners,
        step_summaries=step_rows,
        completion_summary={"completed": sum(1 for s in spec.step_refs if s.status == STEP_COMPLETED), "total": spec.total_steps},
        recommended_actions=actions,
        proxy_notes=[TRAINING_DELIVERY_NOTE, "Simulation/speech/group metrics are non-official when referenced."],
        metadata={},
    )


def recompute_assignment_status(spec: AssignmentSpec) -> str:
    if not spec.step_refs:
        return spec.status
    if all(s.status == STEP_COMPLETED for s in spec.step_refs):
        return AS_COMPLETED
    if any(s.status not in ("pending",) for s in spec.step_refs):
        return AS_IN_PROGRESS
    return spec.status
