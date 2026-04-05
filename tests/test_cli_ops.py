"""Ops CLI smoke (Typer)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.offline_build.cli.commands import app as cli_app
from app.ops.settings import get_ops_settings
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


def test_validate_env_cli(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "snapshots"
    root.mkdir()
    for sub in ("sess", "eval", "fb", "bundles", "audio", "speech_reports"):
        (tmp_path / sub).mkdir()
    monkeypatch.setenv("SNAPSHOT_ROOT", str(root))
    monkeypatch.setenv("SESSION_STORAGE_DIR", str(tmp_path / "sess"))
    monkeypatch.setenv("AUDIO_STORAGE_DIR", str(tmp_path / "audio"))
    monkeypatch.setenv("SPEECH_REPORT_DIR", str(tmp_path / "speech_reports"))
    monkeypatch.setenv("EVAL_REPORT_DIR", str(tmp_path / "eval"))
    monkeypatch.setenv("FEEDBACK_REPORT_DIR", str(tmp_path / "fb"))
    monkeypatch.setenv("BUNDLE_DIR", str(tmp_path / "bundles"))
    monkeypatch.setenv("DEFAULT_PROVIDER", "mock")
    get_ops_settings.cache_clear()
    r = CliRunner().invoke(cli_app, ["validate-env"], catch_exceptions=False)
    assert r.exit_code == 0


def test_list_artifacts_cli(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SNAPSHOT_ROOT", str(tmp_path / "snapshots"))
    (tmp_path / "snapshots").mkdir(parents=True)
    get_ops_settings.cache_clear()
    r = CliRunner().invoke(cli_app, ["list-artifacts", "--kind", "snapshot"], catch_exceptions=False)
    assert r.exit_code == 0


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_export_import_bundle_cli(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    snap_root = tmp_path / "snapshots"
    snap_root.mkdir()
    monkeypatch.setenv("SNAPSHOT_ROOT", str(snap_root))
    get_ops_settings.cache_clear()
    z = tmp_path / "b.zip"
    r1 = CliRunner().invoke(
        cli_app,
        ["export-snapshot-bundle", "--snapshot-dir", str(SNAPSHOT_V2), "--output-file", str(z)],
        catch_exceptions=False,
    )
    assert r1.exit_code == 0
    r2 = CliRunner().invoke(
        cli_app,
        ["import-snapshot-bundle", "--bundle-file", str(z), "--on-conflict", "rename"],
        catch_exceptions=False,
    )
    assert r2.exit_code == 0


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_run_smoke_cli(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SNAPSHOT_ROOT", str(Path(SNAPSHOT_V2).parent))
    monkeypatch.setenv("SESSION_STORAGE_DIR", str(tmp_path / "sessions"))
    monkeypatch.setenv("AUDIO_STORAGE_DIR", str(tmp_path / "audio"))
    monkeypatch.setenv("SPEECH_REPORT_DIR", str(tmp_path / "speech_reports"))
    (tmp_path / "audio").mkdir(parents=True, exist_ok=True)
    (tmp_path / "speech_reports").mkdir(parents=True, exist_ok=True)
    get_ops_settings.cache_clear()
    r = CliRunner().invoke(
        cli_app,
        [
            "run-smoke",
            "--snapshot-id",
            "dev_snapshot_v2",
            "--topic-id",
            "tc-campus-ai",
            "--provider",
            "mock",
            "--runtime-profile",
            "default",
        ],
        catch_exceptions=False,
    )
    assert r.exit_code == 0
