"""review_pack_case scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_review_pack(result: EvalResult) -> EvalResult:
    review_items_graded = result.details.get("review_items_graded", 0)
    total_review_items = result.details.get("total_review_items", 1)
    score = review_items_graded / total_review_items
    result.score = score
    result.passed = score > 0.5
    return result
