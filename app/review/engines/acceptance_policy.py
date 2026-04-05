"""Minimal validation before accepting a review submission."""

from __future__ import annotations

from app.review.schemas.pack import ReviewPack
from app.review.schemas.reviewer import ReviewerProfile
from app.review.schemas.report import HumanReview


def can_submit(*, pack: ReviewPack | None, reviewer: ReviewerProfile | None, hr: HumanReview) -> None:
    if pack is None:
        raise ValueError("review pack not found")
    if reviewer is None:
        raise ValueError("reviewer not found")
    if hr.reviewer_id != reviewer.reviewer_id:
        raise ValueError("reviewer_id mismatch")
    if hr.review_pack_id != pack.review_pack_id:
        raise ValueError("review_pack_id mismatch")
