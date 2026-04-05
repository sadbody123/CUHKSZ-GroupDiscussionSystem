"""CLI for practice modes, drills, and assessment simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.group_service import GroupService
from app.application.mode_service import ModeService
from app.application.session_service import SessionService
from app.logging import setup_logging
from app.modes.loaders.yaml_loader import get_mode_registry


def register_mode_cli(app: typer.Typer) -> None:
    @app.command("list-modes")
    def list_modes_cmd() -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_modes(), ensure_ascii=False, indent=2))

    @app.command("show-mode")
    def show_mode_cmd(mode_id: str = typer.Option(..., "--mode-id")) -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        r = svc.get_mode(mode_id)
        if not r:
            typer.echo("mode not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))

    @app.command("list-presets")
    def list_presets_cmd() -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_presets(), ensure_ascii=False, indent=2))

    @app.command("show-preset")
    def show_preset_cmd(preset_id: str = typer.Option(..., "--preset-id")) -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        r = svc.get_preset(preset_id)
        if not r:
            typer.echo("preset not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))

    @app.command("list-assessment-templates")
    def list_at_cmd() -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_assessment_templates(), ensure_ascii=False, indent=2))

    @app.command("show-assessment-template")
    def show_at_cmd(template_id: str = typer.Option(..., "--template-id")) -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        r = svc.get_assessment_template(template_id)
        if not r:
            typer.echo("template not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))

    @app.command("generate-drills")
    def gen_drills_cmd(learner_id: str = typer.Option(..., "--learner-id")) -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        try:
            rows = svc.generate_drills_for_learner(learner_id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))

    @app.command("mode-status")
    def mode_status_cmd(session_id: str = typer.Option(..., "--session-id")) -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        try:
            st = svc.get_mode_status(session_id)
        except Exception as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e
        typer.echo(json.dumps(st, ensure_ascii=False, indent=2))

    @app.command("export-mode-report")
    def export_mode_report_cmd(
        session_id: str = typer.Option(..., "--session-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        svc = ModeService(AppConfig.from_env())
        rep = svc.load_or_build_mode_report(session_id, persist_if_built=True)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        typer.echo(str(output_file.resolve()))

    @app.command("run-simulated-exam")
    def run_sim_exam_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
        topic_id: str = typer.Option(..., "--topic-id", "-t"),
        template_id: str = typer.Option(..., "--template-id"),
        provider: str = typer.Option("mock", "--provider", "-p"),
        skip_prep: bool = typer.Option(False, "--skip-prep"),
        roster_template_id: Optional[str] = typer.Option(None, "--roster-template-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        sessions = SessionService(cfg)
        disc = DiscussionService(cfg, sessions)
        fb = FeedbackService(sessions)
        ctx = sessions.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance=None,
            provider_name=provider,
            mode_id="assessment_simulation",
            preset_id="assessment_4p",
            assessment_template_id=template_id,
            roster_template_id=roster_template_id,
            user_participant_id="for_a",
            source="simulated_exam",
        )
        if not skip_prep:
            disc.submit_user_turn(ctx.session_id, "Prep complete: I am ready to start the practice simulation.")
        disc.submit_user_turn(ctx.session_id, "Simulation intro: stating my stance briefly.")
        disc.run_next_turn(ctx.session_id)
        disc.auto_run_discussion(ctx.session_id, max_steps=3, auto_fill_user=True)
        report = fb.generate_feedback(ctx.session_id)
        msvc = ModeService(cfg, sessions)
        msvc.maybe_auto_mode_report(ctx.session_id)
        gsvc = GroupService(cfg, sessions)
        gsvc.maybe_auto_group_report(ctx.session_id)
        typer.echo(
            json.dumps(
                {
                    "session_id": ctx.session_id,
                    "coach_report": report.model_dump(),
                    "mode_status": msvc.get_mode_status(ctx.session_id),
                    "group_balance": gsvc.get_group_balance(ctx.session_id),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
