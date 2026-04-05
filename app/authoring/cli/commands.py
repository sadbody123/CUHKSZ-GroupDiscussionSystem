"""Authoring CLI (registered on main Typer app)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.authoring_service import AuthoringService
from app.application.config import AppConfig
from app.application.session_service import SessionService
from app.logging import setup_logging


def register_authoring_cli(app: typer.Typer) -> None:
    @app.command("list-authorable-artifacts")
    def list_authorable_artifacts_cmd(
        artifact_type: Optional[str] = typer.Option(None, "--artifact-type"),
        source_type: Optional[str] = typer.Option(None, "--source-type"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rows = svc.list_authorable_artifacts(artifact_type=artifact_type, source_type=source_type)
        typer.echo(json.dumps([r.model_dump() for r in rows], ensure_ascii=False, indent=2))

    @app.command("create-draft")
    def create_draft_cmd(
        artifact_type: str = typer.Option(..., "--artifact-type"),
        artifact_id: str = typer.Option(..., "--artifact-id"),
        draft_id: str = typer.Option(..., "--draft-id"),
        author_id: Optional[str] = typer.Option(None, "--author-id"),
        as_derivative: bool = typer.Option(False, "--as-derivative"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        d = svc.create_draft(
            draft_id=draft_id,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            author_id=author_id,
            as_derivative=as_derivative,
        )
        typer.echo(json.dumps(d.model_dump(), ensure_ascii=False, indent=2))

    @app.command("create-blank-draft")
    def create_blank_draft_cmd(
        artifact_type: str = typer.Option(..., "--artifact-type"),
        draft_id: str = typer.Option(..., "--draft-id"),
        author_id: Optional[str] = typer.Option(None, "--author-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        d = svc.create_blank_draft(draft_id=draft_id, artifact_type=artifact_type, author_id=author_id)
        typer.echo(json.dumps(d.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-drafts")
    def list_drafts_cmd() -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rows = svc.list_drafts()
        typer.echo(json.dumps([d.model_dump() for d in rows], ensure_ascii=False, indent=2))

    @app.command("show-draft")
    def show_draft_cmd(draft_id: str = typer.Option(..., "--draft-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        d = svc.get_draft(draft_id)
        typer.echo(json.dumps(d.model_dump(), ensure_ascii=False, indent=2))

    @app.command("validate-draft")
    def validate_draft_cmd(draft_id: str = typer.Option(..., "--draft-id")) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rep = svc.validate_draft(draft_id)
        typer.echo(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2))

    @app.command("preview-draft")
    def preview_draft_cmd(
        draft_id: str = typer.Option(..., "--draft-id"),
        preview_kind: str = typer.Option("pack_walkthrough", "--preview-kind"),
        snapshot_id: Optional[str] = typer.Option(None, "--snapshot-id"),
        provider: str = typer.Option("mock", "--provider"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        res = svc.preview_draft(
            draft_id,
            preview_kind=preview_kind,
            snapshot_id=snapshot_id,
            provider_name=provider,
        )
        typer.echo(json.dumps(res.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-patch-proposals")
    def list_patch_proposals_cmd() -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rows = svc.list_patch_proposals()
        typer.echo(json.dumps([p.model_dump() for p in rows], ensure_ascii=False, indent=2))

    @app.command("generate-patch-proposals")
    def generate_patch_proposals_cmd(
        source_type: str = typer.Option(..., "--source-type"),
        source_id: str = typer.Option(..., "--source-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rows = svc.generate_patch_proposals(source_type=source_type, source_id=source_id)
        typer.echo(json.dumps([p.model_dump() for p in rows], ensure_ascii=False, indent=2))

    @app.command("apply-patch-to-draft")
    def apply_patch_to_draft_cmd(
        draft_id: str = typer.Option(..., "--draft-id"),
        patch_id: str = typer.Option(..., "--patch-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        d = svc.apply_patch_to_draft(draft_id, patch_id)
        typer.echo(json.dumps(d.model_dump(), ensure_ascii=False, indent=2))

    @app.command("publish-draft")
    def publish_draft_cmd(
        draft_id: str = typer.Option(..., "--draft-id"),
        published_version: str = typer.Option(..., "--published-version"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rec = svc.publish_draft(draft_id, published_version=published_version)
        typer.echo(json.dumps(rec.model_dump(), ensure_ascii=False, indent=2))

    @app.command("list-publications")
    def list_publications_cmd(
        artifact_type: Optional[str] = typer.Option(None, "--artifact-type"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        rows = svc.list_publications(artifact_type=artifact_type)
        typer.echo(json.dumps([r.model_dump() for r in rows], ensure_ascii=False, indent=2))

    @app.command("show-publication")
    def show_publication_cmd(
        publication_id: str = typer.Option(..., "--publication-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        r = svc.get_publication(publication_id)
        typer.echo(json.dumps(r.model_dump(), ensure_ascii=False, indent=2))

    @app.command("export-authored-artifact")
    def export_authored_artifact_cmd(
        publication_id: str = typer.Option(..., "--publication-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        svc = AuthoringService(cfg, SessionService(cfg))
        out = svc.export_published_artifact(publication_id, output_file)
        typer.echo(json.dumps({"written": str(out)}, ensure_ascii=False, indent=2))
