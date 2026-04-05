"""override_merge_case scoring hook."""

from __future__ import annotations

from app.evals.schemas.result import EvalResult


def score_override_merge(result: EvalResult) -> EvalResult:
    return result
