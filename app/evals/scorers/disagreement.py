"""disagreement_case scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_disagreement(result: EvalResult) -> EvalResult:
    opposing_views_count = result.details.get("opposing_views_count", 0)
    rebuttal_count = result.details.get("rebuttal_count", 0)
    score = min(1.0, (opposing_views_count * 0.4 + rebuttal_count * 0.6) / 3)
    result.score = score
    result.passed = score > 0.3
    return result
