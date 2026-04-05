from __future__ import annotations

from app.learner.aggregation.trend_analyzer import build_skill_scores_from_timeline


def test_trend_improving() -> None:
    pts = [
        {
            "created_at": "2026-01-01T00:00:00+00:00",
            "skill_scores": {"interaction": 40.0},
        },
        {
            "created_at": "2026-01-02T00:00:00+00:00",
            "skill_scores": {"interaction": 55.0},
        },
    ]
    skills = build_skill_scores_from_timeline(pts, recent_window=2, baseline_window=1)
    inter = next(s for s in skills if s.skill_id == "interaction")
    assert inter.trend in ("improving", "stable", "unknown")
