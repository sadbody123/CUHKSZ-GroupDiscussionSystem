from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from app.offline_build.cli.commands import app


def test_review_cli_help() -> None:
    runner = CliRunner()
    r = runner.invoke(app, ["create-reviewer", "--help"])
    assert r.exit_code == 0
