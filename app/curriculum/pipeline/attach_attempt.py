"""Attach session to step and persist attempt."""

from __future__ import annotations

from app.curriculum.schemas.assignment import AssignmentSpec
from app.curriculum.schemas.attempt import AssignmentAttempt


def merge_step_session(spec: AssignmentSpec, pack_step_id: str, session_id: str, attempt: AssignmentAttempt) -> AssignmentSpec:
    for s in spec.step_refs:
        if s.pack_step_id == pack_step_id:
            s.latest_session_id = session_id
            s.attempt_ids.append(attempt.attempt_id)
            s.status = "attempted"
            s.completion_summary = attempt.outcome_summary
            break
    return spec
