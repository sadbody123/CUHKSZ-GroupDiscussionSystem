"""Review subsystem configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from app.application.config import AppConfig
from app.ops.settings import UnifiedSettings, get_ops_settings


class ReviewPaths(BaseModel):
    reviewer_root: Path
    review_root: Path
    review_packs_dir: Path
    submissions_dir: Path
    calibration_dir: Path
    reviewed_outputs_dir: Path
    queue_index_path: Path


def review_paths(settings: UnifiedSettings | None = None) -> ReviewPaths:
    s = settings or get_ops_settings()
    return review_paths_from_roots(s.reviewer_storage_dir.resolve(), s.review_storage_dir.resolve())


def review_paths_from_app_config(cfg: AppConfig) -> ReviewPaths:
    return review_paths_from_roots(cfg.reviewer_storage_dir, cfg.review_storage_dir)


def review_paths_from_roots(reviewer_root: Path, review_root: Path) -> ReviewPaths:
    root = review_root.resolve()
    rr = reviewer_root.resolve()
    return ReviewPaths(
        reviewer_root=rr,
        review_root=root,
        review_packs_dir=root / "review_packs",
        submissions_dir=root / "submissions",
        calibration_dir=root / "calibration",
        reviewed_outputs_dir=root / "reviewed_outputs",
        queue_index_path=root / "queue_index.json",
    )


class ReviewConfig(BaseModel):
    enable_review_workspace: bool = True
    auto_create_review_pack_after_feedback: bool = False
    default_review_rubric_id: str | None = None
    review_queue_max_items: int = 500
    enable_override_merge: bool = True
    calibration_delta_warn_threshold: float = 0.35

    @classmethod
    def from_settings(cls, s: UnifiedSettings | None = None) -> ReviewConfig:
        o = s or get_ops_settings()
        return cls(
            enable_review_workspace=o.enable_review_workspace,
            auto_create_review_pack_after_feedback=o.auto_create_review_pack_after_feedback,
            default_review_rubric_id=o.default_review_rubric_id,
            review_queue_max_items=o.review_queue_max_items,
            enable_override_merge=o.enable_override_merge,
            calibration_delta_warn_threshold=o.calibration_delta_warn_threshold,
        )

    @classmethod
    def from_app_config(cls, cfg: AppConfig) -> ReviewConfig:
        return cls(
            enable_review_workspace=cfg.enable_review_workspace,
            auto_create_review_pack_after_feedback=cfg.auto_create_review_pack_after_feedback,
            default_review_rubric_id=cfg.default_review_rubric_id,
            review_queue_max_items=cfg.review_queue_max_items,
            enable_override_merge=cfg.enable_override_merge,
            calibration_delta_warn_threshold=cfg.calibration_delta_warn_threshold,
        )
