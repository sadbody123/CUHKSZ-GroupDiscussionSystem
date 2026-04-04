"""Runtime CLI smoke tests (Typer CliRunner)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.offline_build.cli.commands import app

ROOT = Path(__file__).resolve().parent.parent
SNAP = ROOT / "app" / "knowledge" / "snapshots" / "dev_snapshot_v2"
RUNTIME_FIX = ROOT / "tests" / "fixtures" / "runtime"


pytestmark = pytest.mark.skipif(
    not (SNAP / "manifest.json").exists(),
    reason="dev_snapshot_v2 not built",
)


def test_cli_list_topics():
    runner = CliRunner()
    r = runner.invoke(app, ["list-topics", "--snapshot-dir", str(SNAP)])
    assert r.exit_code == 0
    assert "tc-campus-ai" in r.stdout or "topic" in r.stdout.lower()


def test_cli_show_topic():
    runner = CliRunner()
    r = runner.invoke(
        app,
        ["show-topic", "--snapshot-dir", str(SNAP), "--topic-id", "tc-campus-ai"],
    )
    assert r.exit_code == 0
    assert "AI on campus" in r.stdout


def test_cli_retrieve_context():
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "retrieve-context",
            "--snapshot-dir",
            str(SNAP),
            "--topic-id",
            "tc-campus-ai",
            "--role",
            "ally",
            "--phase",
            "discussion",
            "--top-k",
            "3",
        ],
    )
    assert r.exit_code == 0
    assert "pedagogy_items" in r.stdout


def test_cli_plan_turn():
    runner = CliRunner()
    tr = RUNTIME_FIX / "sample_transcript.json"
    r = runner.invoke(
        app,
        [
            "plan-turn",
            "--snapshot-dir",
            str(SNAP),
            "--topic-id",
            "tc-campus-ai",
            "--phase",
            "discussion",
            "--last-role",
            "user",
            "--transcript-file",
            str(tr),
        ],
    )
    assert r.exit_code == 0
    assert "next_role" in r.stdout


def test_cli_analyze_transcript():
    runner = CliRunner()
    tr = RUNTIME_FIX / "sample_transcript.json"
    r = runner.invoke(
        app,
        [
            "analyze-transcript",
            "--snapshot-dir",
            str(SNAP),
            "--topic-id",
            "tc-campus-ai",
            "--transcript-file",
            str(tr),
        ],
    )
    assert r.exit_code == 0
    assert "metrics" in r.stdout
