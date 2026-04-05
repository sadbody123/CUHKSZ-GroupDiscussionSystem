"""CLI for multi-seat group simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.group_service import GroupService
from app.application.session_service import SessionService
from app.logging import setup_logging


def register_group_cli(app: typer.Typer) -> None:
    @app.command("list-roster-templates")
    def list_roster_templates_cmd() -> None:
        setup_logging()
        svc = GroupService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_roster_templates(), ensure_ascii=False, indent=2))

    @app.command("show-roster-template")
    def show_roster_template_cmd(roster_template_id: str = typer.Option(..., "--roster-template-id")) -> None:
        setup_logging()
        svc = GroupService(AppConfig.from_env())
        r = svc.get_roster_template(roster_template_id)
        if not r:
            typer.echo("roster template not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))

    @app.command("show-roster")
    def show_roster_cmd(session_id: str = typer.Option(..., "--session-id")) -> None:
        setup_logging()
        svc = GroupService(AppConfig.from_env())
        try:
            typer.echo(json.dumps(svc.get_session_roster(session_id), ensure_ascii=False, indent=2))
        except Exception as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e

    @app.command("show-balance")
    def show_balance_cmd(session_id: str = typer.Option(..., "--session-id")) -> None:
        setup_logging()
        svc = GroupService(AppConfig.from_env())
        try:
            typer.echo(json.dumps(svc.get_group_balance(session_id), ensure_ascii=False, indent=2))
        except Exception as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1) from e

    @app.command("export-group-report")
    def export_group_report_cmd(
        session_id: str = typer.Option(..., "--session-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        svc = GroupService(AppConfig.from_env())
        raw = svc.get_group_report_payload(session_id)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        typer.echo(str(output_file.resolve()))

    @app.command("run-group-smoke")
    def run_group_smoke_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
        topic_id: str = typer.Option(..., "--topic-id", "-t"),
        roster_template_id: str = typer.Option("gd_4p_balanced", "--roster-template-id"),
        user_participant_id: str = typer.Option("for_a", "--user-participant-id"),
        provider: str = typer.Option("mock", "--provider", "-p"),
    ) -> None:
        """Minimal group simulation smoke test."""
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
            roster_template_id=roster_template_id,
            user_participant_id=user_participant_id,
            source="group_smoke",
        )
        disc.submit_user_turn(ctx.session_id, "Group smoke: user turn from my seat.")
        disc.run_next_turn(ctx.session_id)
        disc.auto_run_discussion(ctx.session_id, max_steps=3, auto_fill_user=True)
        report = fb.generate_feedback(ctx.session_id)
        gsvc = GroupService(cfg, sessions)
        gsvc.maybe_auto_group_report(ctx.session_id)
        typer.echo(
            json.dumps(
                {
                    "session_id": ctx.session_id,
                    "coach_report": report.model_dump(),
                    "group_balance": gsvc.get_group_balance(ctx.session_id),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
