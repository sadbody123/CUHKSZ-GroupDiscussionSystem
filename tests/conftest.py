"""Shared pytest paths."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_config
from app.api.main import create_app
from app.application.config import AppConfig, get_app_config

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
    return base.model_copy(update={"session_storage_dir": tmp_path / "sessions"})


@pytest.fixture
def api_client(api_test_config: AppConfig) -> Generator[TestClient, None, None]:
    app = create_app()
    app.dependency_overrides[get_config] = lambda: api_test_config
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
