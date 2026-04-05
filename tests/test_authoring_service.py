from __future__ import annotations

from app.application.authoring_service import AuthoringService
from app.application.config import AppConfig
from app.application.session_service import SessionService


def test_authoring_derivative_and_publish(api_test_config: AppConfig, tmp_path) -> None:
    cfg = api_test_config.model_copy(
        update={
            "authoring_root_dir": tmp_path / "authoring",
            "authoring_published_runtime_profile_dir": tmp_path / "authoring" / "published" / "runtime_profiles",
            "authoring_published_misc_dir": tmp_path / "authoring" / "published" / "artifacts",
        }
    )
    svc = AuthoringService(cfg, SessionService(cfg))
    svc.create_derivative_draft(
        draft_id="tderiv1",
        artifact_type="curriculum_pack",
        base_artifact_id="foundation_gd_pack",
        author_id="t",
    )
    d = svc.get_draft("tderiv1")
    assert d.content.get("pack_id") != "foundation_gd_pack"
    svc.validate_draft("tderiv1")
    pub = svc.publish_draft("tderiv1", published_version="1.0.0")
    assert pub.publication_id
