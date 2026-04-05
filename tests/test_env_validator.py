"""Environment validator."""

from __future__ import annotations

import pytest

from app.ops.env_validator import validate_environment
from app.ops.settings import UnifiedSettings, get_ops_settings


def test_validate_env_structure(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "snapshots"
    root.mkdir()
    monkeypatch.setenv("SNAPSHOT_ROOT", str(root))
    monkeypatch.setenv("SESSION_STORAGE_DIR", str(tmp_path / "sess"))
    monkeypatch.setenv("EVAL_REPORT_DIR", str(tmp_path / "eval"))
    monkeypatch.setenv("FEEDBACK_REPORT_DIR", str(tmp_path / "fb"))
    monkeypatch.setenv("BUNDLE_DIR", str(tmp_path / "bundles"))
    monkeypatch.setenv("DEFAULT_PROVIDER", "mock")
    get_ops_settings.cache_clear()
    r = validate_environment()
    assert "checks" in r
    assert "warnings" in r
    assert "errors" in r
    assert r["overall_status"] in ("ok", "error")
    assert isinstance(r["checks"], list)
    assert r.get("platform")
    assert r.get("path_style_note")


def test_validate_env_missing_profile_warns(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "snapshots"
    root.mkdir()
    for sub in ("sess", "eval", "fb", "bundles"):
        (tmp_path / sub).mkdir()
    monkeypatch.setenv("SNAPSHOT_ROOT", str(root))
    monkeypatch.setenv("SESSION_STORAGE_DIR", str(tmp_path / "sess"))
    monkeypatch.setenv("EVAL_REPORT_DIR", str(tmp_path / "eval"))
    monkeypatch.setenv("FEEDBACK_REPORT_DIR", str(tmp_path / "fb"))
    monkeypatch.setenv("BUNDLE_DIR", str(tmp_path / "bundles"))
    monkeypatch.setenv("DEFAULT_RUNTIME_PROFILE", "does_not_exist_profile")
    monkeypatch.setenv("DEFAULT_PROVIDER", "mock")
    get_ops_settings.cache_clear()
    r = validate_environment()
    assert r["overall_status"] == "error"
    assert any("default_runtime_profile" in e for e in r["errors"])
