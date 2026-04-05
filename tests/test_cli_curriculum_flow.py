from __future__ import annotations

import json

from typer.testing import CliRunner

from app.offline_build.cli.commands import app as root_app


def test_cli_list_curriculum_packs() -> None:
    runner = CliRunner()
    r = runner.invoke(root_app, ["list-curriculum-packs"])
    assert r.exit_code == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    ids = [x["pack_id"] for x in data]
    assert "foundation_gd_pack" in ids
