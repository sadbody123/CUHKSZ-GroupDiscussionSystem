"""Assemble explainable recommendations."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.learner.config import LearnerConfig
from app.learner.schemas.learner import LearnerProfile
from app.learner.schemas.recommendation import RecommendationItem
from app.learner.recommendation.mode_selector import select_mode_recommendations
from app.learner.recommendation.pedagogy_selector import select_pedagogy_recommendations
from app.learner.recommendation.profile_selector import select_profile_recommendations
from app.learner.recommendation.topic_selector import select_topic_recommendations


def build_recommendations(
    profile: LearnerProfile,
    snapshot_dir: Path,
    *,
    cfg: LearnerConfig,
    practiced_topic_ids: set[str] | None = None,
    max_turn_words_hint: int = 0,
    has_audio_history: bool = False,
) -> list[RecommendationItem]:
    weak = list(profile.weak_skills or [])
    practiced = practiced_topic_ids or set()
    items: list[RecommendationItem] = []
    items.extend(
        select_topic_recommendations(
            snapshot_dir,
            weak_skills=weak,
            practiced_topic_ids=practiced,
            max_items=min(5, cfg.max_recommendation_items),
        )
    )
    items.extend(
        select_pedagogy_recommendations(
            snapshot_dir,
            weak_skills=weak,
            max_items=min(6, cfg.max_recommendation_items),
        )
    )
    items.extend(
        select_profile_recommendations(
            weak_skills=weak,
            current_profile=profile.current_runtime_profile_id,
            max_turn_words_hint=max_turn_words_hint,
        )
    )
    items.extend(
        select_mode_recommendations(
            weak_skills=weak,
            has_audio_history=has_audio_history,
        )
    )
    # micro drills
    drills = [
        (
            "micro_drill_short_turn",
            "30-second short turn",
            "Speak or write one claim + one reason in under 30 seconds (timer).",
            {"focus": "turn_concision"},
        ),
        (
            "micro_drill_examples",
            "Example sandwich drill",
            "Claim → example → link back (one paragraph).",
            {"focus": "example_usage"},
        ),
        (
            "micro_drill_polite_rebuttal",
            "Polite rebuttal frames",
            "Practice: 'I see your point; however…' + one counter-reason.",
            {"focus": "rebuttal_clarity"},
        ),
    ]
    for did, title, desc, meta in drills:
        if weak and meta["focus"] not in weak[:4]:
            continue
        items.append(
            RecommendationItem(
                recommendation_id=str(uuid.uuid4()),
                recommendation_type="micro_drill",
                title=title,
                reason=desc,
                priority="medium",
                linked_topic_ids=[],
                linked_pedagogy_item_ids=[],
                suggested_runtime_profile_id=None,
                suggested_mode="text",
                metadata=meta,
            )
        )
    return items[: cfg.max_recommendation_items]
