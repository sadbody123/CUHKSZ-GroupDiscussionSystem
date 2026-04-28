"""launch_bridge scoring hook."""

from __future__ import annotations

from app.evals.scorers.common import bool_score
from app.evals.schemas.result import EvalResult


def score_launch_bridge(result: EvalResult) -> EvalResult:
    launch_success_count = result.details.get("launch_success_count", 0)
    launch_attempt_count = result.details.get("launch_attempt_count", 1)
    score = launch_success_count / launch_attempt_count
    result.score = score
    result.passed = score > 0.8
    return result
