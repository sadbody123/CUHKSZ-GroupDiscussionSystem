"""Learner subsystem configuration (from ops settings)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.ops.settings import UnifiedSettings, get_ops_settings


@dataclass(frozen=True)
class LearnerConfig:
    enable_analytics: bool
    storage_dir: Path
    default_plan_horizon: int
    max_recommendation_items: int
    recent_window: int
    baseline_window: int
    auto_ingest_on_feedback: bool
    enable_ui_panels: bool


def get_learner_config(settings: UnifiedSettings | None = None) -> LearnerConfig:
    s = settings or get_ops_settings()
    return LearnerConfig(
        enable_analytics=s.enable_learner_analytics,
        storage_dir=s.learner_storage_dir.resolve(),
        default_plan_horizon=s.default_learning_plan_horizon,
        max_recommendation_items=s.learner_recommendation_max_items,
        recent_window=s.learner_recent_window,
        baseline_window=s.learner_baseline_window,
        auto_ingest_on_feedback=s.auto_ingest_session_to_learner,
        enable_ui_panels=s.enable_learner_ui_panels,
    )
