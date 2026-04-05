"""Shared pytest paths."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_config, get_handover_service, get_stability_service
from app.application.handover_service import HandoverService
from app.application.stability_service import StabilityService
from app.api.main import create_app
from app.application.config import AppConfig, _default_curriculum_builtin_dir, get_app_config
from app.ops.settings import get_ops_settings


@pytest.fixture(autouse=True)
def _clear_ops_settings_cache() -> Generator[None, None, None]:
    get_ops_settings.cache_clear()
    yield
    get_ops_settings.cache_clear()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_EXPORTS = PROJECT_ROOT / "tests" / "fixtures" / "datahub_exports"
FIXTURE_PEDAGOGY = PROJECT_ROOT / "tests" / "fixtures" / "pedagogy"
FIXTURE_TOPIC_CARDS = PROJECT_ROOT / "tests" / "fixtures" / "topic_cards"
FIXTURE_RUNTIME = PROJECT_ROOT / "tests" / "fixtures" / "runtime"
# Phase-2 snapshot built locally or in CI (optional)
SNAPSHOT_V2 = PROJECT_ROOT / "app" / "knowledge" / "snapshots" / "dev_snapshot_v2"
HAS_SNAPSHOT_V2 = (SNAPSHOT_V2 / "manifest.json").is_file()


@pytest.fixture
def fixture_exports_dir() -> Path:
    return FIXTURE_EXPORTS


@pytest.fixture
def fixture_pedagogy_dir() -> Path:
    return FIXTURE_PEDAGOGY


@pytest.fixture
def fixture_topic_cards_dir() -> Path:
    return FIXTURE_TOPIC_CARDS


@pytest.fixture
def fixture_runtime_dir() -> Path:
    return FIXTURE_RUNTIME


@pytest.fixture
def snapshot_v2_dir() -> Path:
    return SNAPSHOT_V2


@pytest.fixture
def api_test_config(tmp_path: Path) -> AppConfig:
    base = get_app_config()
    return base.model_copy(
        update={
            "session_storage_dir": tmp_path / "sessions",
            "learner_storage_dir": tmp_path / "learners",
            "speech_report_dir": tmp_path / "speech_reports",
            "mode_reports_dir": tmp_path / "mode_reports",
            "group_reports_dir": tmp_path / "group_reports",
            "review_storage_dir": tmp_path / "reviews",
            "reviewer_storage_dir": tmp_path / "reviewers",
            "curriculum_pack_builtin_dir": _default_curriculum_builtin_dir(),
            "curriculum_custom_pack_dir": tmp_path / "curriculum_custom",
            "assignment_storage_dir": tmp_path / "assignments",
            "authoring_root_dir": tmp_path / "authoring",
            "authoring_published_runtime_profile_dir": tmp_path / "authoring" / "published" / "runtime_profiles",
            "authoring_published_misc_dir": tmp_path / "authoring" / "published" / "artifacts",
            "active_release_profile": "v1_demo",
        }
    )


@pytest.fixture
def api_client(api_test_config: AppConfig) -> Generator[TestClient, None, None]:
    app = create_app()
    app.dependency_overrides[get_config] = lambda: api_test_config
    app.dependency_overrides[get_stability_service] = lambda: StabilityService(api_test_config)
    app.dependency_overrides[get_handover_service] = lambda: HandoverService(api_test_config)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
