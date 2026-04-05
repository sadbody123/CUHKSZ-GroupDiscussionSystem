"""Runtime profile suggestions (rule-based)."""

from __future__ import annotations

from app.learner.schemas.recommendation import RecommendationItem


def select_profile_recommendations(
    *,
    weak_skills: list[str],
    current_profile: str | None,
    max_turn_words_hint: int = 0,
) -> list[RecommendationItem]:
    out: list[RecommendationItem] = []
    if "turn_concision" in weak_skills or max_turn_words_hint > 220:
        out.append(
            RecommendationItem(
                recommendation_id="profile_concise",
                recommendation_type="runtime_profile",
                title="Try a concise profile",
                reason="Long turns or weak concision — shorter coach prompts help tighten responses.",
                priority="high",
                linked_topic_ids=[],
                linked_pedagogy_item_ids=[],
                suggested_runtime_profile_id="concise",
                suggested_mode=None,
                metadata={"hint": "max_turn_words"},
            )
        )
    if "interaction" in weak_skills[:2]:
        out.append(
            RecommendationItem(
                recommendation_id="profile_strict_coach",
                recommendation_type="runtime_profile",
                title="Stricter coaching feedback",
                reason="Interaction signals are low — structured coach feedback may help turn-taking.",
                priority="medium",
                linked_topic_ids=[],
                linked_pedagogy_item_ids=[],
                suggested_runtime_profile_id="strict_coach",
                suggested_mode=None,
                metadata={},
            )
        )
    if not out:
        out.append(
            RecommendationItem(
                recommendation_id="profile_balanced_default",
                recommendation_type="runtime_profile",
                title="Balanced runtime profile",
                reason="Default balanced practice profile when no strong override applies.",
                priority="low",
                linked_topic_ids=[],
                linked_pedagogy_item_ids=[],
                suggested_runtime_profile_id="balanced",
                suggested_mode=None,
                metadata={},
            )
        )
    if current_profile:
        for r in out:
            r.metadata = {**(r.metadata or {}), "previous_profile": current_profile}
    return out[:3]
