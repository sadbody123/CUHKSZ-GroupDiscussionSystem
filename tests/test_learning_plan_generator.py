from __future__ import annotations

from app.learner.planning.plan_generator import generate_learning_plan
from app.learner.schemas.recommendation import RecommendationItem


def test_generate_learning_plan_steps() -> None:
    recs = [
        RecommendationItem(
            recommendation_id="1",
            recommendation_type="topic",
            title="t",
            reason="r",
            linked_topic_ids=["topic_a"],
        ),
        RecommendationItem(
            recommendation_id="2",
            recommendation_type="mode",
            title="m",
            reason="r",
            suggested_mode="text",
        ),
    ]
    plan = generate_learning_plan("L", ["example_usage"], recs, horizon=4)
    assert len(plan.steps) == 4
