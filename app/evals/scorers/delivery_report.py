"""delivery_report scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_delivery_report(result: EvalResult) -> EvalResult:
    required_fields_present = result.details.get("required_fields_present", 0)
    total_required_fields = result.details.get("total_required_fields", 1)
    score = required_fields_present / total_required_fields
    result.score = score
    result.passed = score > 0.8
    return result
