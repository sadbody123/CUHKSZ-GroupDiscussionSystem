from __future__ import annotations

from app.curriculum.engines.attempt_tracker import build_attempt


def test_build_attempt() -> None:
    a = build_attempt(
        assignment_id="a1",
        assignment_step_id="s1",
        session_id="sess",
        learner_id="l",
        topic_id="t",
    )
    assert a.attempt_id and a.session_id == "sess"
