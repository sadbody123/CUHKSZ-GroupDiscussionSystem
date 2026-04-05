"""Build assignment attempt records."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.curriculum.schemas.attempt import AssignmentAttempt
from app.runtime.schemas.session import SessionContext


def build_attempt(
    *,
    assignment_id: str,
    assignment_step_id: str,
    session_id: str,
    learner_id: str | None,
    topic_id: str | None,
) -> AssignmentAttempt:
    now = datetime.now(timezone.utc).isoformat()
    return AssignmentAttempt(
        attempt_id=str(uuid.uuid4()),
        assignment_id=assignment_id,
        assignment_step_id=assignment_step_id,
        learner_id=learner_id,
        session_id=session_id,
        topic_id=topic_id,
        created_at=now,
        completed_at=now,
        success_checks=[],
        outcome_summary={"training_attempt": True},
        artifact_refs={"session_id": session_id},
        metadata={},
    )
