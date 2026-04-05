"""Typer CLI for offline build and snapshot validation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from app.config import get_settings
from app.logging import setup_logging
from app.offline_build.build_snapshot.validators import validate_snapshot_dir
from app.offline_build.pipeline import run_offline_pipeline

app = typer.Typer(no_args_is_help=True, add_completion=False)


def _run_build(
    input_dir: Path,
    snapshot_id: str,
    pedagogy_dir: Optional[Path],
    topic_card_dir: Optional[Path],
) -> Path:
    setup_logging()
    settings = get_settings()
    return run_offline_pipeline(
        input_dir,
        snapshot_id,
        settings=settings,
        pedagogy_dir=pedagogy_dir,
        topic_card_dir=topic_card_dir,
    )


@app.command("build-offline")
def build_offline(
    input_dir: Path = typer.Option(
        ...,
        "--input-dir",
        "-i",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Directory containing Datahub JSON/CSV table exports",
    ),
    snapshot_id: str = typer.Option(
        ...,
        "--snapshot-id",
        "-s",
        help="Snapshot identifier (output folder name)",
    ),
    pedagogy_dir: Optional[Path] = typer.Option(
        None,
        "--pedagogy-dir",
        help="Directory with pedagogy JSONL files (rules, rubric, ...); enables knowledge layer",
    ),
    topic_card_dir: Optional[Path] = typer.Option(
        None,
        "--topic-card-dir",
        help="Directory with topic card YAML/JSON; enables knowledge layer",
    ),
) -> None:
    """Build an offline snapshot from exported table files (optional pedagogy / topic cards)."""
    out = _run_build(input_dir, snapshot_id, pedagogy_dir, topic_card_dir)
    typer.echo(f"Snapshot written to: {out}")


@app.command("build-knowledge")
def build_knowledge(
    input_dir: Path = typer.Option(
        ...,
        "--input-dir",
        "-i",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
    pedagogy_dir: Optional[Path] = typer.Option(
        None,
        "--pedagogy-dir",
        help="Pedagogy JSONL directory",
    ),
    topic_card_dir: Optional[Path] = typer.Option(
        None,
        "--topic-card-dir",
        help="Topic card YAML/JSON directory",
    ),
) -> None:
    """Alias for ``build-offline`` with explicit knowledge-layer intent (requires pedagogy and/or topic dirs)."""
    if pedagogy_dir is None and topic_card_dir is None:
        typer.echo(
            "ERROR: specify at least one of --pedagogy-dir or --topic-card-dir for build-knowledge.",
            err=True,
        )
        raise typer.Exit(code=1)
    out = _run_build(input_dir, snapshot_id, pedagogy_dir, topic_card_dir)
    typer.echo(f"Snapshot written to: {out}")


@app.command("validate-snapshot")
def validate_snapshot(
    snapshot_dir: Path = typer.Option(
        ...,
        "--snapshot-dir",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Snapshot directory (contains manifest.json)",
    ),
) -> None:
    """Validate snapshot files and JSONL parseability."""
    setup_logging()
    res = validate_snapshot_dir(snapshot_dir)
    if res.ok:
        typer.echo("OK: snapshot validation passed.")
    else:
        typer.echo("FAILED: snapshot validation errors.", err=True)
    for e in res.errors:
        typer.echo(f"  ERROR: {e}", err=True)
    for w in res.warnings:
        typer.echo(f"  WARN: {w}")
    if not res.ok:
        raise typer.Exit(code=1)


from app.runtime.cli.commands import register_runtime_cli as _register_runtime_cli

_register_runtime_cli(app)


@app.command("run-api")
def run_api(
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload"),
) -> None:
    """Start FastAPI with Uvicorn (phase 5)."""
    import uvicorn

    uvicorn.run("app.api.main:app", host=host, port=port, reload=reload)


from app.evals.cli.commands import register_eval_cli as _register_eval_cli

_register_eval_cli(app)

from app.ops.cli.commands import register_ops_cli as _register_ops_cli

_register_ops_cli(app)

from app.indexing.cli.commands import register_flat_index_commands as _register_index_cli

_register_index_cli(app)

from app.audio.cli.commands import register_audio_cli as _register_audio_cli

_register_audio_cli(app)

from app.learner.cli.commands import register_learner_cli as _register_learner_cli

_register_learner_cli(app)

from app.modes.cli.commands import register_mode_cli as _register_mode_cli

_register_mode_cli(app)

from app.group_sim.cli.commands import register_group_cli as _register_group_cli

_register_group_cli(app)

from app.review.cli.commands import register_review_cli as _register_review_cli

_register_review_cli(app)

from app.curriculum.cli.commands import register_curriculum_cli as _register_curriculum_cli

_register_curriculum_cli(app)

from app.authoring.cli.commands import register_authoring_cli as _register_authoring_cli

_register_authoring_cli(app)

from app.release.cli.commands import register_release_cli as _register_release_cli

_register_release_cli(app)

from app.stability.cli.commands import register_stability_cli as _register_stability_cli

_register_stability_cli(app)

from app.handover.cli.commands import register_handover_cli as _register_handover_cli

_register_handover_cli(app)


@app.command("run-ui")
def run_ui(
    api_base_url: str = typer.Option("http://127.0.0.1:8000", "--api-base-url"),
) -> None:
    """Start Streamlit UI (expects API at --api-base-url)."""
    import os
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    script = root / "app" / "ui" / "streamlit_app.py"
    env = os.environ.copy()
    env["UI_API_BASE_URL"] = api_base_url
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(script),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    raise SystemExit(subprocess.call(cmd, cwd=str(root), env=env))
