"""Handover / final delivery CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.handover_service import HandoverService
from app.logging import setup_logging


def register_handover_cli(app: typer.Typer) -> None:
    @app.command("build-release-manifest")
    def build_release_manifest_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        out = svc.build_release_manifest(profile_id)
        typer.echo(json.dumps({k: v for k, v in out.items() if k != "path"}, ensure_ascii=False, indent=2))

    @app.command("build-bom")
    def build_bom_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        out = svc.build_bom(profile_id)
        typer.echo(json.dumps({k: v for k, v in out.items() if k != "json_path"}, ensure_ascii=False, indent=2))

    @app.command("build-demo-kit")
    def build_demo_kit_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        typer.echo(json.dumps(svc.build_demo_kit(profile_id, output_dir), ensure_ascii=False, indent=2))

    @app.command("build-handover-kit")
    def build_handover_kit_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        typer.echo(json.dumps(svc.build_handover_kit(profile_id, output_dir), ensure_ascii=False, indent=2))

    @app.command("verify-delivery")
    def verify_delivery_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        rep = svc.verify_delivery(profile_id)
        typer.echo(json.dumps(rep, ensure_ascii=False, indent=2))
        raise typer.Exit(0 if rep.get("overall_status") != "blocked" else 1)

    @app.command("export-acceptance-evidence")
    def export_acceptance_evidence_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        p = svc.export_acceptance_markdown(profile_id, output_file)
        typer.echo(json.dumps({"written": str(p)}, ensure_ascii=False, indent=2))

    @app.command("export-release-docs-bundle")
    def export_release_docs_bundle_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        typer.echo(json.dumps(svc.export_release_docs_bundle(profile_id, output_dir), ensure_ascii=False, indent=2))

    @app.command("package-final-release")
    def package_final_release_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        typer.echo(json.dumps(svc.package_final_release(profile_id, output_file), ensure_ascii=False, indent=2))

    @app.command("run-final-demo")
    def run_final_demo_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        snapshot_id: str = typer.Option("dev_snapshot_v2", "--snapshot-id"),
        provider: str = typer.Option("mock", "--provider"),
    ) -> None:
        setup_logging()
        svc = HandoverService(AppConfig.from_env())
        out = svc.run_final_demo(profile_id, snapshot_id, provider_name=provider)
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))
        raise typer.Exit(0 if out.get("demo", {}).get("success", False) else 1)
