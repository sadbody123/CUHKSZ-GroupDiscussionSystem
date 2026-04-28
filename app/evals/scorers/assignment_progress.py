"""assignment_progress scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_assignment_progress(result: EvalResult) -> EvalResult:
    completed_steps = result.details.get("completed_steps", 0)
    total_steps = result.details.get("total_steps", 1)
    score = completed_steps / total_steps
    result.score = score
    result.passed = score > 0.5
    return result
