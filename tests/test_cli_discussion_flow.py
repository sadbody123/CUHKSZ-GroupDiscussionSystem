"""Discussion CLI with mock provider."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.offline_build.cli.commands import app
from tests.conftest import HAS_SNAPSHOT_V2, PROJECT_ROOT

SNAP = PROJECT_ROOT / "app" / "knowledge" / "snapshots" / "dev_snapshot_v2"

pytestmark = pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")


def test_discussion_cli_flow(tmp_path: Path):
    runner = CliRunner()
    store = tmp_path / "st"
    r = runner.invoke(
        app,
        [
            "create-session",
            "--snapshot-dir",
            str(SNAP),
            "--topic-id",
            "tc-campus-ai",
            "--user-stance",
            "for",
            "--provider",
            "mock",
            "--storage-root",
            str(store),
        ],
    )
    assert r.exit_code == 0, r.stdout + r.stderr
    sid = r.stdout.strip()
    r2 = runner.invoke(
        app,
        [
            "submit-user-turn",
            "--session-id",
            sid,
            "--text",
            "I believe AI can help students brainstorm.",
            "--storage-root",
            str(store),
        ],
    )
    assert r2.exit_code == 0
    r3 = runner.invoke(app, ["run-next-turn", "--session-id", sid, "--storage-root", str(store)])
    assert r3.exit_code == 0
    r4 = runner.invoke(app, ["generate-feedback", "--session-id", sid, "--storage-root", str(store)])
    assert r4.exit_code == 0
    assert "text" in r4.stdout
