"""plan_to_pack scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_plan_to_pack(result: EvalResult) -> EvalResult:
    plans_mapped = result.details.get("plans_mapped", 0)
    total_plans = result.details.get("total_plans", 1)
    score = plans_mapped / total_plans
    result.score = score
    result.passed = score > 0.5
    return result
