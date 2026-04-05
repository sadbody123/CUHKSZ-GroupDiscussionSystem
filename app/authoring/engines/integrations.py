"""Cross-subsystem hooks for authoring."""

from __future__ import annotations

from app.application.config import AppConfig
from app.authoring.config import authoring_paths_from_app_config
from app.authoring.store import DraftStore, PatchStore, PublicationStore, rebuild_authoring_index


def rebuild_index(cfg: AppConfig) -> dict:
    paths = authoring_paths_from_app_config(cfg)
    return rebuild_authoring_index(
        index_path=paths.index_path,
        drafts=DraftStore(paths.drafts_dir),
        patches=PatchStore(paths.patches_dir),
        publications=PublicationStore(
            paths.publications_dir,
            paths.published_root,
            project_root=cfg.project_root,
        ),
    )


def note_review_service_available() -> bool:
    return True
