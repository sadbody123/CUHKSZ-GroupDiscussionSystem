"""Deterministic step completion checks from session artifacts."""

from __future__ import annotations

from typing import Any

from app.curriculum.schemas.pack import CurriculumPackStep
from app.curriculum.constants import STEP_ATTEMPTED, STEP_COMPLETED
from app.runtime.schemas.session import SessionContext


def evaluate_step_completion(ctx: SessionContext, step: CurriculumPackStep) -> tuple[str, dict[str, Any]]:
    """Return (status, summary) — training completion only."""
    summary: dict[str, Any] = {"turn_count": len(ctx.turns), "has_coach": bool(ctx.coach_report)}
    if not ctx.turns and not ctx.coach_report:
        return "pending", summary

    crit = [c.lower() for c in (step.success_criteria or [])]
    if not crit:
        status = STEP_COMPLETED if ctx.coach_report and ctx.turns else STEP_ATTEMPTED
        summary["criteria_matched"] = status == STEP_COMPLETED
        return status, summary

    ok = True
    if "transcript" in crit:
        ok = ok and len(ctx.turns) > 0
    if "feedback" in crit or "coach_report" in crit:
        ok = ok and bool(ctx.coach_report)
    if "speech_report" in crit:
        ok = ok and bool(ctx.speech_report_id)
    if "mode_report" in crit:
        ok = ok and bool(ctx.mode_report_id)
    if "group_balance_report" in crit:
        ok = ok and bool(ctx.group_balance_report_id)

    status = STEP_COMPLETED if ok else STEP_ATTEMPTED
    summary["criteria_matched"] = ok
    return status, summary
