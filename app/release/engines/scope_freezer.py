"""Scope freeze suggestions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.release.constants import DECISION_DEFER, DECISION_EXPERIMENTAL, DECISION_HIDE, DECISION_KEEP
from app.release.engines.capability_registry import all_capabilities
from app.release.engines.feature_gate import is_capability_enabled, load_profile_or_default
from app.release.schemas.report import ScopeDecision, ScopeFreezeSummary


def build_scope_freeze_summary(profile_id: str) -> ScopeFreezeSummary:
    profile = load_profile_or_default(profile_id)
    decisions: list[ScopeDecision] = []
    for c in all_capabilities():
        enabled = is_capability_enabled(profile, c.capability_id)
        exp = c.capability_id in profile.experimental_capabilities
        if not enabled:
            dec = DECISION_HIDE if c.stability in ("stable", "beta") else DECISION_DEFER
            reason = "Disabled in release profile"
        elif exp:
            dec = DECISION_EXPERIMENTAL
            reason = "Marked experimental in profile"
        else:
            dec = DECISION_KEEP
            reason = "Enabled for profile"
        decisions.append(
            ScopeDecision(
                decision_id=f"sd_{uuid.uuid4().hex[:8]}",
                capability_id=c.capability_id,
                decision=dec,
                reason=reason,
                impact=[c.area],
            )
        )
    lines = [f"Scope freeze for profile `{profile_id}`", ""]
    for d in decisions[:30]:
        lines.append(f"- {d.capability_id}: {d.decision} — {d.reason}")
    return ScopeFreezeSummary(
        profile_id=profile_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        decisions=decisions,
        summary_text="\n".join(lines),
        metadata={},
    )
