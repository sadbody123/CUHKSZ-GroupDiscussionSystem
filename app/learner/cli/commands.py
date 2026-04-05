"""CLI commands for learner analytics (phase 11)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.learner_service import LearnerService
from app.application.session_service import SessionService
from app.logging import setup_logging


def register_learner_cli(app: typer.Typer) -> None:
    @app.command("create-learner")
    def create_learner_cmd(
        learner_id: str = typer.Option(..., "--learner-id"),
        display_name: Optional[str] = typer.Option(None, "--display-name"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = LearnerService(cfg)
        try:
            p = svc.create_learner(learner_id, display_name=display_name)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-learners")
    def list_learners_cmd() -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        rows = svc.list_learners()
        typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))

    @app.command("show-learner-profile")
    def show_learner_profile_cmd(learner_id: str = typer.Option(..., "--learner-id")) -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        p = svc.get_learner_profile(learner_id)
        if not p:
            typer.echo("learner not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))

    @app.command("attach-session-to-learner")
    def attach_session_cmd(
        learner_id: str = typer.Option(..., "--learner-id"),
        session_id: str = typer.Option(..., "--session-id"),
    ) -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        try:
            r = svc.attach_session_to_learner(learner_id, session_id, ingest=True)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))

    @app.command("rebuild-learner-profile")
    def rebuild_learner_cmd(learner_id: str = typer.Option(..., "--learner-id")) -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        try:
            svc.rebuild_learner_profile(learner_id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps({"ok": True, "learner_id": learner_id}, ensure_ascii=False))

    @app.command("recommend-practice")
    def recommend_practice_cmd(learner_id: str = typer.Option(..., "--learner-id")) -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        try:
            items = svc.get_recommendations(learner_id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps([x.model_dump() for x in items], ensure_ascii=False, indent=2))

    @app.command("generate-learning-plan")
    def gen_plan_cmd(
        learner_id: str = typer.Option(..., "--learner-id"),
        horizon: int = typer.Option(4, "--horizon"),
    ) -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        try:
            plan = svc.generate_learning_plan(learner_id, horizon=horizon, persist=True)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps(plan.model_dump(), ensure_ascii=False, indent=2))

    @app.command("export-learner-report")
    def export_report_cmd(
        learner_id: str = typer.Option(..., "--learner-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        svc = LearnerService(AppConfig.from_env())
        try:
            svc.export_learner_report(learner_id, output_file=output_file)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(str(output_file.resolve()))
