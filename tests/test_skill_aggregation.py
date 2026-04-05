from __future__ import annotations

from pathlib import Path

from app.learner.aggregation.skill_aggregator import compute_session_skill_scores
from app.runtime.schemas.session import SessionContext


def test_compute_session_skill_scores_fixture() -> None:
    root = Path(__file__).resolve().parent
    ctx = SessionContext.model_validate_json(
        (root / "fixtures/learners/session_exports/learner_fixture_sess_01.json").read_text(encoding="utf-8")
    )
    scores, m = compute_session_skill_scores(ctx, speech_report=None)
    assert "example_usage" in scores
    assert m["has_speech_aggregate"] is False
