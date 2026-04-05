"""Evaluate soft constraints on user turns."""

from __future__ import annotations

from typing import Any

from app.modes.schemas.drill import DrillSpec
from app.modes.schemas.mode import PracticeMode
from app.runtime.schemas.session import SessionContext


def evaluate_user_turn_constraints(
    ctx: SessionContext,
    text: str,
    *,
    mode: PracticeMode | None,
    drill: DrillSpec | None,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    policy = (mode.constraint_policy if mode else {}) or {}
    soft_max = int(policy.get("max_words_per_turn_soft") or 400)
    wc = len(text.split())
    if wc > soft_max:
        events.append(
            {
                "type": "long_turn_warning",
                "severity": "low",
                "detail": f"Turn length {wc} words exceeds soft cap {soft_max}.",
                "word_count": wc,
            }
        )
    if drill and drill.success_criteria:
        events.append(
            {
                "type": "drill_reminder",
                "severity": "info",
                "detail": "Refer to drill success criteria in mode_state.",
                "drill_id": drill.drill_id,
            }
        )
    return events


def merge_constraint_events(ctx: SessionContext, new_events: list[dict[str, Any]]) -> None:
    ms = dict(ctx.mode_state or {})
    ev = list(ms.get("constraint_events") or [])
    ev.extend(new_events)
    ms["constraint_events"] = ev[-200:]
    ctx.mode_state = ms
