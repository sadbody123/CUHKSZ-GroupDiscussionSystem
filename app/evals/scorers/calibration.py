"""calibration_case scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_calibration(result: EvalResult) -> EvalResult:
    calibration_drift = result.details.get("calibration_drift", 1.0)
    score = max(0.0, 1.0 - calibration_drift)
    result.score = score
    result.passed = score > 0.7
    return result
