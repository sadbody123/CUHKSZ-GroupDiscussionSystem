from __future__ import annotations

import pytest

from app.learner.config import LearnerConfig
from app.learner.recommendation.engine import build_recommendations
from app.learner.schemas.learner import LearnerProfile
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_build_recommendations_smoke() -> None:
    snapshot_dir = SNAPSHOT_V2
    p = LearnerProfile(
        learner_id="x",
        weak_skills=["example_usage", "interaction"],
        strong_skills=[],
        session_ids=["s1"],
    )
    cfg = LearnerConfig(
        enable_analytics=True,
        storage_dir=snapshot_dir,
        default_plan_horizon=4,
        max_recommendation_items=12,
        recent_window=3,
        baseline_window=3,
        auto_ingest_on_feedback=False,
        enable_ui_panels=True,
    )
    items = build_recommendations(
        p,
        snapshot_dir,
        cfg=cfg,
        practiced_topic_ids=set(),
        max_turn_words_hint=0,
        has_audio_history=False,
    )
    types = {x.recommendation_type for x in items}
    assert "topic" in types
    assert "mode" in types
