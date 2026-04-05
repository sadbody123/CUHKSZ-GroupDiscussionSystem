"""calibration_case scoring hook."""

from __future__ import annotations

from app.evals.schemas.result import EvalResult


def score_calibration(result: EvalResult) -> EvalResult:
    return result
