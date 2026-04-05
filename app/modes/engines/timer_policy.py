"""Soft timer state derived from session timestamps (no background jobs)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modes.schemas.assessment import AssessmentTemplate
from app.modes.schemas.mode import PracticeMode
from app.runtime.schemas.session import SessionContext


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_timer_state(
    ctx: SessionContext,
    *,
    mode: PracticeMode | None,
    template: AssessmentTemplate | None,
) -> dict[str, Any]:
    created = _parse_iso(str(ctx.metadata.get("created_at") or ""))
    now = datetime.now(timezone.utc)
    elapsed = (now - created).total_seconds() if created else 0.0
    out: dict[str, Any] = {
        "elapsed_seconds": round(elapsed, 3),
        "now_iso": now.isoformat(),
        "kind": (mode.timer_policy or {}).get("type") if mode else "none",
    }
    if template:
        out["prep_seconds"] = template.prep_seconds
        out["discussion_seconds"] = template.discussion_seconds
        out["intro_seconds_per_side"] = template.intro_seconds_per_side
        out["summary_seconds_per_side"] = template.summary_seconds_per_side
        # Soft phase estimate (sequential budget — heuristic)
        budgets = [
            ("prep", float(template.prep_seconds or 0)),
            ("intro", float(template.intro_seconds_per_side or 0) * 2),
            ("discussion", float(template.discussion_seconds or 0)),
            ("summary", float(template.summary_seconds_per_side or 0) * 2),
        ]
        acc = 0.0
        phase = "prep"
        remaining_in_phase = 0.0
        for name, dur in budgets:
            if elapsed <= acc + dur or dur == 0:
                phase = name
                remaining_in_phase = max(0.0, acc + dur - elapsed)
                break
            acc += dur
        else:
            phase = "post"
            remaining_in_phase = 0.0
        out["assessment_phase_estimate"] = phase
        out["remaining_in_phase_seconds"] = round(remaining_in_phase, 3)
    return out
