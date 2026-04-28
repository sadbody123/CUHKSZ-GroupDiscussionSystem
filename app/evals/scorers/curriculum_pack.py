"""curriculum_pack scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_curriculum_pack(result: EvalResult) -> EvalResult:
    step_completion_rate = result.details.get("step_completion_rate", 0.0)
    score = step_completion_rate
    result.score = score
    result.passed = score > 0.5
    return result
