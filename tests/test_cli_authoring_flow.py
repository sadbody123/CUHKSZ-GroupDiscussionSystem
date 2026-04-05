from __future__ import annotations

from typer.testing import CliRunner

from app.offline_build.cli.commands import app as root_app


def test_cli_list_authorable_artifacts() -> None:
    runner = CliRunner()
    r = runner.invoke(root_app, ["list-authorable-artifacts", "--artifact-type", "curriculum_pack"])
    assert r.exit_code == 0, r.stdout + r.stderr
