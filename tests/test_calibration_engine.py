from __future__ import annotations

from app.review.engines.calibration_engine import build_calibration_report
from app.review.schemas.report import HumanReview


def test_calibration_smoke() -> None:
    hr = HumanReview(
        review_id="a",
        review_pack_id="p",
        reviewer_id="r",
        created_at="2026-01-01T00:00:00Z",
        summary_notes=["note"],
    )
    rep = build_calibration_report(
        review_pack_id="p",
        session_id="s",
        review_id="a",
        coach_report={"strengths": ["s"], "risks": ["r"]},
        human=hr,
    )
    assert rep.overall_agreement
    assert rep.results
