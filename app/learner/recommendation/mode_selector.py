"""Recommend text / audio / mixed practice mode."""

from __future__ import annotations

from app.learner.constants import SPEECH_PROXY_SKILL_IDS
from app.learner.schemas.recommendation import RecommendationItem


def select_mode_recommendations(
    *,
    weak_skills: list[str],
    has_audio_history: bool,
) -> list[RecommendationItem]:
    speech_weak = [s for s in weak_skills if s in SPEECH_PROXY_SKILL_IDS]
    mode = "text"
    reason = "Focus on discussion language and structure with text-first practice."
    if speech_weak and has_audio_history:
        mode = "mixed"
        reason = "Speech proxy metrics are weak and audio history exists — alternate text and short audio turns."
    elif speech_weak and not has_audio_history:
        mode = "text"
        reason = "Speech proxies are weak but there is little audio history — start with text, then add short audio."
    elif not speech_weak and has_audio_history:
        mode = "audio"
        reason = "Speech proxies are acceptable — continue audio practice for delivery."
    return [
        RecommendationItem(
            recommendation_id="mode_primary",
            recommendation_type="mode",
            title=f"Suggested mode: {mode}",
            reason=reason,
            priority="high",
            linked_topic_ids=[],
            linked_pedagogy_item_ids=[],
            suggested_runtime_profile_id=None,
            suggested_mode=mode,
            metadata={"has_audio_history": has_audio_history},
        )
    ]
