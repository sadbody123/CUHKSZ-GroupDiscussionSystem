"""Track coarse mode progress on the session."""

from __future__ import annotations

from typing import Any

from app.runtime.schemas.session import SessionContext


def update_progress_after_turn(ctx: SessionContext) -> None:
    ms = dict(ctx.mode_state or {})
    ms["discussion_turns"] = len([t for t in ctx.turns if t.speaker_role.lower() == "user"])
    ms["total_turns"] = len(ctx.turns)
    ms["session_phase"] = ctx.phase
    ctx.mode_state = ms


def mark_stage(ctx: SessionContext, stage: str, *, detail: str | None = None) -> None:
    ms = dict(ctx.mode_state or {})
    seq = list(ms.get("stage_log") or [])
    seq.append({"stage": stage, "detail": detail})
    ms["stage_log"] = seq[-50:]
    ms["current_stage"] = stage
    ctx.mode_state = ms


def success_checks_from_drill(ctx: SessionContext, checks: list[dict[str, Any]]) -> None:
    ms = dict(ctx.mode_state or {})
    sc = list(ms.get("success_checks") or [])
    sc.extend(checks)
    ms["success_checks"] = sc[-50:]
    ctx.mode_state = ms
