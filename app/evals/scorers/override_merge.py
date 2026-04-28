"""override_merge_case scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_override_merge(result: EvalResult) -> EvalResult:
    merge_conflicts = result.details.get("merge_conflicts", 0)
    total_overrides = result.details.get("total_overrides", 1)
    score = 1.0 - merge_conflicts / total_overrides
    result.score = score
    result.passed = score > 0.7
    return result
