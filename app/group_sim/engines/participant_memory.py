"""Per-participant deterministic memory keys."""

from __future__ import annotations

from typing import Any

from app.runtime.schemas.session import SessionContext


def ensure_memory_root(ctx: SessionContext) -> dict[str, Any]:
    pm = ctx.participant_memory_state or {}
    if "_meta" not in pm:
        pm["_meta"] = {}
    ctx.participant_memory_state = pm
    return pm


def get_participant_slice(ctx: SessionContext, participant_id: str) -> dict[str, Any]:
    pm = ensure_memory_root(ctx)
    key = f"p:{participant_id}"
    if key not in pm:
        pm[key] = {
            "recent_turn_ids": [],
            "claimed_points": [],
            "used_examples": [],
            "repeated_topics": [],
            "last_phase_spoken": None,
            "has_done_intro": False,
            "has_done_summary": False,
        }
    return pm[key]


def record_turn(
    ctx: SessionContext,
    *,
    participant_id: str,
    turn_id: str,
    phase: str,
    text: str,
) -> None:
    sl = get_participant_slice(ctx, participant_id)
    rt = list(sl.get("recent_turn_ids") or [])
    rt.append(turn_id)
    sl["recent_turn_ids"] = rt[-30:]
    sl["last_phase_spoken"] = phase
    if phase == "intro":
        sl["has_done_intro"] = True
    if phase == "summary":
        sl["has_done_summary"] = True
    wc = len(text.split())
    if wc > 180:
        sl["last_long_turn"] = True
    else:
        sl["last_long_turn"] = False


def memory_summary_for_prompt(ctx: SessionContext, participant_id: str) -> str:
    sl = get_participant_slice(ctx, participant_id)
    parts = [
        f"intro_done={sl.get('has_done_intro')}",
        f"summary_done={sl.get('has_done_summary')}",
        f"recent_turns={len(sl.get('recent_turn_ids') or [])}",
    ]
    return "; ".join(parts)
