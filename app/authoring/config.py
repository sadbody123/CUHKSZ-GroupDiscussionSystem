"""Authoring path helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.application.config import AppConfig


@dataclass(frozen=True)
class AuthoringPaths:
    drafts_dir: Path
    patches_dir: Path
    publications_dir: Path
    validation_reports_dir: Path
    preview_results_dir: Path
    published_root: Path
    index_path: Path


def authoring_paths_from_app_config(cfg: AppConfig) -> AuthoringPaths:
    root = cfg.authoring_root_dir.resolve()
    return AuthoringPaths(
        drafts_dir=root / "drafts",
        patches_dir=root / "patches",
        publications_dir=root / "publications",
        validation_reports_dir=root / "validation_reports",
        preview_results_dir=root / "preview_results",
        published_root=root / "published",
        index_path=root / "index.json",
    )
