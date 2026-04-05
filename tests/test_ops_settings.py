"""Unified ops settings."""

from __future__ import annotations

import pytest

from app.ops.settings import UnifiedSettings, get_ops_settings


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in (
        "APP_ENV",
        "LOG_LEVEL",
        "SNAPSHOT_ROOT",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(k, raising=False)
    get_ops_settings.cache_clear()
    s = UnifiedSettings()
    assert s.app_name
    assert s.default_provider == "mock"
    assert s.openai_api_key is None


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SNAPSHOT_ROOT", str(tmp_path / "snaps"))
    monkeypatch.setenv("DEFAULT_PROVIDER", "mock")
    get_ops_settings.cache_clear()
    s = get_ops_settings()
    assert s.app_env == "test"
    assert s.log_level == "DEBUG"
    assert s.snapshot_root == tmp_path / "snaps"

