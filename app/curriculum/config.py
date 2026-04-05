"""Curriculum paths from AppConfig."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from app.application.config import AppConfig


class CurriculumPaths(BaseModel):
    pack_builtin_dir: Path
    pack_custom_dir: Path
    assignment_root: Path


def curriculum_paths_from_app_config(cfg: AppConfig) -> CurriculumPaths:
    return CurriculumPaths(
        pack_builtin_dir=cfg.curriculum_pack_builtin_dir,
        pack_custom_dir=cfg.curriculum_custom_pack_dir,
        assignment_root=cfg.assignment_storage_dir,
    )
