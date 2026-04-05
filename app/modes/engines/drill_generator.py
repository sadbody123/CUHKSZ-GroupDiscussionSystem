"""Deterministic drill recommendations for a learner."""

from __future__ import annotations

from typing import Any

from app.learner.schemas.learner import LearnerProfile
from app.modes.loaders.yaml_loader import get_mode_registry
from app.modes.schemas.drill import DrillSpec


def generate_drills_for_profile(
    profile: LearnerProfile | None,
    *,
    max_drills: int = 8,
) -> list[dict[str, Any]]:
    reg = get_mode_registry()
    weak = list(profile.weak_skills or []) if profile else []
    out: list[dict[str, Any]] = []
    for did, spec in reg.drills.items():
        score = 0
        for sk in weak:
            if sk in spec.target_skills:
                score += 2
        if weak and score == 0:
            continue
        if not weak:
            score = 1
        reason = (
            f"Matched weak skills {set(weak).intersection(set(spec.target_skills))!s} (score={score})."
            if weak
            else "Baseline drill suggestion (no weak-skill profile)."
        )
        out.append(
            {
                "drill_id": spec.drill_id,
                "title": spec.title,
                "objective": spec.objective,
                "target_skills": spec.target_skills,
                "reason": reason,
                "suggested_mode_id": spec.suggested_mode_id,
                "runtime_profile_id": spec.runtime_profile_id,
                "score": score,
            }
        )
    out.sort(key=lambda x: x.get("score", 0), reverse=True)
    return out[:max_drills]


def drill_spec_to_recommendation_dict(spec: DrillSpec) -> dict[str, Any]:
    return {
        "drill_id": spec.drill_id,
        "title": spec.title,
        "objective": spec.objective,
        "target_skills": spec.target_skills,
        "suggested_mode_id": spec.suggested_mode_id,
        "runtime_profile_id": spec.runtime_profile_id,
    }
