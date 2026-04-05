from __future__ import annotations

from app.curriculum.constants import STEP_ATTEMPTED, STEP_COMPLETED
from app.curriculum.engines.completion_engine import evaluate_step_completion
from app.curriculum.schemas.pack import CurriculumPackStep
from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn


def test_completion_transcript_criterion_met() -> None:
    step = CurriculumPackStep(
        step_id="x",
        order=1,
        title="t",
        success_criteria=["transcript"],
    )
    ctx = SessionContext(
        session_id="s",
        turns=[TranscriptTurn(turn_id="1", speaker_role="user", text="hi")],
    )
    status, summary = evaluate_step_completion(ctx, step)
    assert status == STEP_COMPLETED
    assert summary.get("criteria_matched") is True


def test_completion_pending_empty() -> None:
    step = CurriculumPackStep(step_id="x", order=1, title="t", success_criteria=["transcript"])
    ctx = SessionContext(session_id="s", turns=[])
    status, _ = evaluate_step_completion(ctx, step)
    assert status == "pending"
