"""Pipeline: rebuild calibration report."""

from __future__ import annotations

from app.review.constants import PACK_CALIBRATED
from app.review.engines.calibration_engine import build_calibration_report
from app.review.schemas.report import HumanReview
from app.review.store.review_store import ReviewStore


def run_rebuild_calibration(
    *,
    review_pack_id: str,
    review_id: str,
    coach_report: dict | None,
    store: ReviewStore,
) -> object:
    pack = store.load_review_pack(review_pack_id)
    hr = store.load_human_review(review_id)
    if not pack or not hr:
        raise ValueError("pack or review not found")
    rep = build_calibration_report(
        review_pack_id=review_pack_id,
        session_id=pack.session_id,
        review_id=review_id,
        coach_report=coach_report,
        human=hr,
    )
    store.save_calibration_report(rep)
    pack.status = PACK_CALIBRATED
    store.save_review_pack(pack)
    return rep
