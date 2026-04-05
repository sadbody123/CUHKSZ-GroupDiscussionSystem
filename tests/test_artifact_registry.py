"""Artifact registry scan."""

from __future__ import annotations

import json

import pytest

from app.ops.artifacts.registry import ArtifactRegistry
from app.ops.settings import get_ops_settings


def test_registry_scans_snapshots(snapshot_v2_dir, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "snapshots"
    root.mkdir()
    # minimal copy marker: symlink or copy manifest - use real fixture path via env
    monkeypatch.setenv("SNAPSHOT_ROOT", str(snapshot_v2_dir.parent))
    get_ops_settings.cache_clear()
    reg = ArtifactRegistry()
    snaps = reg.list_artifacts(kind="snapshot")
    ids = {s.artifact_id for s in snaps}
    assert "dev_snapshot_v2" in ids
    summary = reg.summarize_by_kind()
    assert summary.get("snapshot", 0) >= 1


def test_registry_session_json(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    sdir = tmp_path / "sessions"
    sdir.mkdir(parents=True)
    (sdir / "sess-1.json").write_text(json.dumps({"session_id": "sess-1", "topic_id": "t"}), encoding="utf-8")
    monkeypatch.setenv("SESSION_STORAGE_DIR", str(sdir))
    monkeypatch.setenv("SNAPSHOT_ROOT", str(tmp_path / "snapshots"))
    (tmp_path / "snapshots").mkdir()
    get_ops_settings.cache_clear()
    reg = ArtifactRegistry()
    rows = reg.list_artifacts(kind="session")
    assert any(r.artifact_id == "sess-1" for r in rows)
