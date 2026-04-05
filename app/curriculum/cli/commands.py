"""CLI for curriculum packs and assignments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.curriculum_service import CurriculumService
from app.application.session_service import SessionService
from app.logging import setup_logging


def register_curriculum_cli(app: typer.Typer) -> None:
    @app.command("list-curriculum-packs")
    def list_curriculum_packs_cmd() -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        rows = svc.list_curriculum_packs()
        typer.echo(json.dumps([p.model_dump() for p in rows], ensure_ascii=False, indent=2))

    @app.command("show-curriculum-pack")
    def show_curriculum_pack_cmd(pack_id: str = typer.Option(..., "--pack-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        try:
            p = svc.get_curriculum_pack(pack_id)
        except ValueError:
            typer.echo("pack not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))

    @app.command("create-assignment")
    def create_assignment_cmd(
        pack_id: str = typer.Option(..., "--pack-id"),
        learner_id: str = typer.Option(..., "--learner-id"),
        created_by: Optional[str] = typer.Option(None, "--created-by"),
        title: str = typer.Option(..., "--title"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        a = svc.create_assignment(
            pack_id=pack_id,
            learner_ids=[learner_id],
            created_by=created_by,
            title=title,
        )
        typer.echo(json.dumps(a.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-assignments")
    def list_assignments_cmd() -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        rows = svc.list_assignments()
        typer.echo(json.dumps([a.model_dump() for a in rows], ensure_ascii=False, indent=2))

    @app.command("show-assignment")
    def show_assignment_cmd(assignment_id: str = typer.Option(..., "--assignment-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        try:
            a = svc.get_assignment(assignment_id)
        except ValueError:
            typer.echo("assignment not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(a.model_dump(), ensure_ascii=False, indent=2))

    @app.command("show-assignment-progress")
    def show_assignment_progress_cmd(assignment_id: str = typer.Option(..., "--assignment-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        try:
            d = svc.get_assignment_progress(assignment_id)
        except ValueError:
            typer.echo("assignment not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(d, ensure_ascii=False, indent=2))

    @app.command("launch-assignment-step")
    def launch_assignment_step_cmd(
        assignment_id: str = typer.Option(..., "--assignment-id"),
        step_id: str = typer.Option(..., "--step-id"),
        snapshot_id: str = typer.Option(..., "--snapshot-id"),
        provider: str = typer.Option("mock", "--provider"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        out = svc.launch_assignment_step_session(
            assignment_id=assignment_id,
            pack_step_id=step_id,
            snapshot_id=snapshot_id,
            provider_name=provider,
        )
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))

    @app.command("attach-session-to-assignment-step")
    def attach_session_cmd(
        assignment_id: str = typer.Option(..., "--assignment-id"),
        step_id: str = typer.Option(..., "--step-id"),
        session_id: str = typer.Option(..., "--session-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        out = svc.attach_session_to_assignment_step(
            assignment_id=assignment_id,
            pack_step_id=step_id,
            session_id=session_id,
        )
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))

    @app.command("generate-assignment-report")
    def generate_assignment_report_cmd(assignment_id: str = typer.Option(..., "--assignment-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        r = svc.generate_assignment_report(assignment_id)
        typer.echo(json.dumps(r.model_dump(), ensure_ascii=False, indent=2))

    @app.command("export-assignment-report")
    def export_assignment_report_cmd(
        assignment_id: str = typer.Option(..., "--assignment-id"),
        output_file: Path = typer.Option(..., "--output-file"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        out = svc.export_assignment_report(assignment_id, output_file=output_file)
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))

    @app.command("create-pack-from-learning-plan")
    def create_pack_from_plan_cmd(
        learner_id: str = typer.Option(..., "--learner-id"),
        horizon: int = typer.Option(3, "--horizon"),
        output_pack_id: str = typer.Option(..., "--output-pack-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = CurriculumService(cfg, SessionService(cfg))
        try:
            p = svc.create_curriculum_pack_from_learning_plan(
                learner_id=learner_id,
                horizon=horizon,
                output_pack_id=output_pack_id,
            )
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))
