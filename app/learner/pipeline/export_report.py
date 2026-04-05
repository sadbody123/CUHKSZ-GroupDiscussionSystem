"""Assemble LearnerReport dict for export."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.learner.schemas.report import LearnerReport


def build_learner_report_dict(
    learner_profile: dict[str, Any],
    progress_points: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
    learning_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    rep = LearnerReport(
        report_id=str(uuid.uuid4()),
        learner_id=str(learner_profile.get("learner_id", "")),
        generated_at=datetime.now(timezone.utc).isoformat(),
        profile_summary=learner_profile,
        progress_points=progress_points,
        recommendations=recommendations,
        learning_plan=learning_plan,
        proxy_limitations=[
            "Skill scores are heuristic training signals from transcript rules and optional speech proxies.",
            "Speech-related metrics are not official pronunciation or delivery grades.",
        ],
    )
    return rep.model_dump()
