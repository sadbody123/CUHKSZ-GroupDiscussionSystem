"""review_pack_case scoring hook (pass-through)."""

from __future__ import annotations

from app.evals.schemas.result import EvalResult


def score_review_pack(result: EvalResult) -> EvalResult:
    return result
