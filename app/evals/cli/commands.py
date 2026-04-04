"""Eval & profile CLI (phase 6)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from app.evals.replay.engine import run_replay
from app.evals.run_suite import compare_profiles, run_eval_suite
from app.runtime.profile_resolver import list_resolved_profile_summaries, resolve_runtime_profile


def register_eval_cli(app: typer.Typer) -> None:
    @app.command("list-profiles")
    def list_profiles_cmd() -> None:
        """List runtime profiles."""
        for row in list_resolved_profile_summaries():
            typer.echo(f"{row['profile_id']}\t{row.get('description') or ''}")

    @app.command("show-profile")
    def show_profile_cmd(
        profile_id: str = typer.Option(..., "--profile-id", "-p"),
    ) -> None:
        """Show merged runtime profile YAML as JSON."""
        import json

        p = resolve_runtime_profile(profile_id)
        typer.echo(json.dumps(p.merged_dict(), ensure_ascii=False, indent=2))

    @app.command("run-evals")
    def run_evals(
        suite_file: Path = typer.Option(..., "--suite-file", exists=True, dir_okay=False),
        snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
        profile_id: str = typer.Option("default", "--profile-id", "-p"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        """Run an eval suite and write reports."""
        run_eval_suite(suite_file=suite_file, snapshot_dir=snapshot_dir, profile_id=profile_id, output_dir=output_dir)
        typer.echo(f"Reports written to {output_dir.resolve()}")

    @app.command("compare-profiles")
    def compare_profiles_cmd(
        suite_file: Path = typer.Option(..., "--suite-file", exists=True),
        snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
        profiles: str = typer.Option(..., "--profiles", help="Space-separated profile ids"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        """Run the same suite across multiple profiles."""
        ids = [p.strip() for p in profiles.split() if p.strip()]
        compare_profiles(suite_file=suite_file, snapshot_dir=snapshot_dir, profiles=ids, output_dir=output_dir)
        typer.echo(f"Comparison report at {output_dir.resolve()}")

    @app.command("replay-session")
    def replay_session_cmd(
        session_file: Path = typer.Option(..., "--session-file", exists=True),
        mode: str = typer.Option("analyze", "--mode", "-m"),
        profile_id: str = typer.Option("default", "--profile-id", "-p"),
        snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        """Replay an exported session JSON."""
        run_replay(
            session_file=session_file,
            mode=mode,
            profile_id=profile_id,
            snapshot_dir=snapshot_dir,
            output_dir=output_dir,
        )
        typer.echo(f"Replay summary written to {output_dir.resolve()}")
