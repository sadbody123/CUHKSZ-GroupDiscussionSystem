from __future__ import annotations

from app.review.engines.override_merger import merge_reviewed_feedback
from app.review.schemas.override import OverrideDecision


def test_merge_appends_strength() -> None:
    base = {"strengths": ["x"], "risks": []}
    ods = [
        OverrideDecision(
            override_id="1",
            target_type="coach_report",
            target_path="strengths",
            action="append",
            new_value=["y"],
            reason="t",
            approved=True,
        )
    ]
    art = merge_reviewed_feedback(
        base_coach_report=base,
        overrides=ods,
        review_id="rv",
        reviewer_id="rev",
        review_pack_id="p",
        session_id="s",
    )
    assert "y" in art.payload.get("strengths", [])
