from __future__ import annotations

from app.application.config import AppConfig
from app.application.curriculum_service import CurriculumService
from app.application.session_service import SessionService


def test_curriculum_service_lists_builtin_pack(api_test_config: AppConfig) -> None:
    svc = CurriculumService(api_test_config, SessionService(api_test_config))
    packs = svc.list_curriculum_packs()
    ids = {p.pack_id for p in packs}
    assert "foundation_gd_pack" in ids


def test_curriculum_service_get_pack(api_test_config: AppConfig) -> None:
    svc = CurriculumService(api_test_config, SessionService(api_test_config))
    p = svc.get_curriculum_pack("foundation_gd_pack")
    assert p.pack_id == "foundation_gd_pack"
    assert len(p.steps) >= 1
