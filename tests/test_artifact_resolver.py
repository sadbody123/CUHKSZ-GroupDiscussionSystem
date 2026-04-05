from __future__ import annotations

from app.application.config import AppConfig
from app.authoring.engines.artifact_resolver import list_authorable_artifacts, load_base_content_for_derivative
from app.authoring.store.publication_store import PublicationStore


def test_list_includes_foundation_pack(api_test_config: AppConfig) -> None:
    pub = PublicationStore(
        api_test_config.authoring_root_dir / "publications",
        api_test_config.authoring_root_dir / "published",
        project_root=api_test_config.project_root,
    )
    rows = list_authorable_artifacts(
        api_test_config,
        artifact_type="curriculum_pack",
        publication_store=pub,
    )
    ids = {r.artifact_id for r in rows}
    assert "foundation_gd_pack" in ids


def test_load_base_curriculum(api_test_config: AppConfig) -> None:
    base = load_base_content_for_derivative(api_test_config, "curriculum_pack", "foundation_gd_pack")
    assert base and base.get("pack_id") == "foundation_gd_pack"
