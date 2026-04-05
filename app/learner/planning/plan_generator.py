"""Build a 3–5 step learning plan from profile + recommendations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.learner.schemas.plan import LearningPlan, LearningPlanStep
from app.learner.schemas.recommendation import RecommendationItem


def _pick_topic(recs: list[RecommendationItem]) -> str | None:
    for r in recs:
        if r.recommendation_type == "topic" and r.linked_topic_ids:
            return r.linked_topic_ids[0]
    return None


def _pick_pedagogy(recs: list[RecommendationItem], n: int = 3) -> list[str]:
    ids: list[str] = []
    for r in recs:
        if r.recommendation_type == "pedagogy":
            ids.extend(r.linked_pedagogy_item_ids)
        if len(ids) >= n:
            break
    return ids[:n]


def _pick_profile(recs: list[RecommendationItem]) -> str | None:
    for r in recs:
        if r.recommendation_type == "runtime_profile" and r.suggested_runtime_profile_id:
            return r.suggested_runtime_profile_id
    return "balanced"


def _pick_mode(recs: list[RecommendationItem]) -> str | None:
    for r in recs:
        if r.recommendation_type == "mode" and r.suggested_mode:
            return r.suggested_mode
    return "text"


def generate_learning_plan(
    learner_id: str,
    weak_skills: list[str],
    recommendations: list[RecommendationItem],
    *,
    horizon: int = 4,
) -> LearningPlan:
    horizon = max(3, min(5, horizon))
    topic = _pick_topic(recommendations)
    ped_ids = _pick_pedagogy(recommendations)
    prof = _pick_profile(recommendations)
    mode = _pick_mode(recommendations)
    steps: list[dict[str, Any]] = []
    ws = weak_skills[:3] if weak_skills else ["interaction"]

    for i in range(horizon):
        focus = ws[min(i, len(ws) - 1)]
        if i == 0:
            title = f"Target weakest skill: {focus}"
            objective = "Short session with explicit examples and concise turns."
            step_mode = "text"
            step_prof = "concise" if focus == "turn_concision" else prof or "balanced"
        elif i == 1:
            title = "Balance interaction and examples"
            objective = "Practice responding to a peer with linkage phrases."
            step_mode = mode or "text"
            step_prof = "balanced"
        elif i == 2:
            title = "Add audio if speech proxies need work"
            objective = "Optional: one short spoken turn with mock ASR (proxy metrics)."
            step_mode = "mixed" if mode in ("mixed", "audio") else "text"
            step_prof = "speech_default" if step_mode != "text" else (prof or "default")
        else:
            title = "Consolidation with stricter feedback"
            objective = "Integrate strengths; request concise coach report."
            step_mode = mode or "text"
            step_prof = "strict_coach"

        st = LearningPlanStep(
            step_id=str(uuid.uuid4()),
            order=i + 1,
            title=title,
            objective=objective,
            topic_id=topic,
            runtime_profile_id=step_prof,
            mode=step_mode,
            focus_skills=[focus],
            linked_pedagogy_item_ids=ped_ids,
            metadata={"generator": "plan_generator_v1"},
        )
        steps.append(st.model_dump())

    from app.learner.planning.templates import PLAN_NOTES_GENERIC

    return LearningPlan(
        plan_id=str(uuid.uuid4()),
        learner_id=learner_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        horizon_sessions=horizon,
        steps=steps,
        notes=list(PLAN_NOTES_GENERIC),
        metadata={"weak_skills": weak_skills},
    )
