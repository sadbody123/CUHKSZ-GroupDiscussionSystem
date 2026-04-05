"""CLI commands for review workspace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.review_service import ReviewService
from app.application.session_service import SessionService
from app.logging import setup_logging


def register_review_cli(app: typer.Typer) -> None:
    @app.command("create-reviewer")
    def create_reviewer_cmd(
        reviewer_id: str = typer.Option(..., "--reviewer-id"),
        display_name: str = typer.Option(..., "--display-name"),
        role_title: Optional[str] = typer.Option(None, "--role-title"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        p = svc.create_reviewer(reviewer_id=reviewer_id, display_name=display_name, role_title=role_title)
        typer.echo(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-reviewers")
    def list_reviewers_cmd() -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        rows = svc.list_reviewers()
        typer.echo(json.dumps([r.model_dump() for r in rows], ensure_ascii=False, indent=2))

    @app.command("create-review-pack")
    def create_review_pack_cmd(session_id: str = typer.Option(..., "--session-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        pack = svc.create_review_pack(session_id)
        typer.echo(json.dumps(pack.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-review-packs")
    def list_review_packs_cmd() -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        rows = svc.list_review_packs()
        typer.echo(json.dumps([p.model_dump() for p in rows], ensure_ascii=False, indent=2))

    @app.command("show-review-pack")
    def show_review_pack_cmd(review_pack_id: str = typer.Option(..., "--review-pack-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        try:
            p = svc.get_review_pack(review_pack_id)
        except ValueError:
            typer.echo("review pack not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))

    @app.command("submit-review")
    def submit_review_cmd(
        review_pack_id: str = typer.Option(..., "--review-pack-id"),
        reviewer_id: str = typer.Option(..., "--reviewer-id"),
        review_file: Path = typer.Option(..., "--review-file", exists=True, dir_okay=False),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        payload = json.loads(review_file.read_text(encoding="utf-8"))
        hr = svc.submit_human_review(
            review_pack_id=review_pack_id,
            reviewer_id=reviewer_id,
            payload=payload,
        )
        typer.echo(json.dumps(hr.model_dump(), ensure_ascii=False, indent=2))

    @app.command("show-review-summary")
    def show_review_summary_cmd(session_id: str = typer.Option(..., "--session-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        typer.echo(json.dumps(svc.get_review_summary(session_id), ensure_ascii=False, indent=2))

    @app.command("compare-ai-vs-human")
    def compare_ai_vs_human_cmd(review_pack_id: str = typer.Option(..., "--review-pack-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        try:
            d = svc.compare_ai_vs_human(review_pack_id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(d, ensure_ascii=False, indent=2))

    @app.command("export-calibration-report")
    def export_calibration_report_cmd(
        review_pack_id: str = typer.Option(..., "--review-pack-id"),
        output_file: Path = typer.Option(..., "--output-file"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        svc.export_review_report(review_pack_id, output_file=output_file, as_markdown=False)
        typer.echo(json.dumps({"written": str(output_file.resolve())}, ensure_ascii=False, indent=2))

    @app.command("export-reviewed-feedback")
    def export_reviewed_feedback_cmd(
        review_pack_id: str = typer.Option(..., "--review-pack-id"),
        output_file: Path = typer.Option(..., "--output-file"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = ReviewService(cfg, SessionService(cfg))
        data = svc.export_reviewed_feedback(review_pack_id)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        typer.echo(json.dumps({"written": str(output_file.resolve())}, ensure_ascii=False, indent=2))
