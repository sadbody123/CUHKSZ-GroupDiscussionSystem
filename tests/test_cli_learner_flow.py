from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.offline_build.cli.commands import app as root_app


def test_create_list_learners_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEARNER_STORAGE_DIR", str(tmp_path / "learners"))
    runner = CliRunner()
    r = runner.invoke(root_app, ["create-learner", "--learner-id", "cli_l1", "--display-name", "X"])
    assert r.exit_code == 0, r.output
    r2 = runner.invoke(root_app, ["list-learners"])
    assert r2.exit_code == 0
    assert "cli_l1" in r2.output
