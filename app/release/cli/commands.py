"""Release / demo CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.release_service import ReleaseService
from app.logging import setup_logging
from app.release.pipeline.build_capability_matrix import build_capability_matrix_json
from app.release.schemas.report import ScopeFreezeSummary


def register_release_cli(app: typer.Typer) -> None:
    @app.command("list-release-profiles")
    def list_release_profiles_cmd() -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        rows = svc.list_release_profiles()
        typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))

    @app.command("show-release-profile")
    def show_release_profile_cmd(profile_id: str = typer.Option(..., "--profile-id")) -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        typer.echo(json.dumps(svc.get_release_profile(profile_id), ensure_ascii=False, indent=2))

    @app.command("list-capabilities")
    def list_capabilities_cmd() -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_capabilities(), ensure_ascii=False, indent=2))

    @app.command("show-capability-matrix")
    def show_capability_matrix_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        pid = profile_id or ReleaseService(AppConfig.from_env()).active_profile_id()
        typer.echo(json.dumps(build_capability_matrix_json(pid), ensure_ascii=False, indent=2))

    @app.command("audit-release-readiness")
    def audit_release_readiness_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        rep = svc.run_readiness_audit(profile_id)
        typer.echo(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2))
        raise typer.Exit(0 if rep.overall_status != "blocked" else 1)

    @app.command("run-demo-scenario")
    def run_demo_scenario_cmd(
        scenario_id: str = typer.Option(..., "--scenario-id"),
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        snapshot_id: str = typer.Option("dev_snapshot_v2", "--snapshot-id"),
        topic_id: str = typer.Option("tc-campus-ai", "--topic-id"),
        provider: str = typer.Option("mock", "--provider"),
    ) -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        r = svc.run_demo_scenario(
            scenario_id,
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider,
        )
        typer.echo(json.dumps(r.model_dump(), ensure_ascii=False, indent=2))
        raise typer.Exit(0 if r.success else 1)

    @app.command("export-demo-bundle")
    def export_demo_bundle_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        out = svc.export_demo_bundle(profile_id, output_dir)
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))

    @app.command("freeze-scope-report")
    def freeze_scope_report_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        s = svc.get_scope_freeze_summary(profile_id)
        typer.echo(json.dumps(s, ensure_ascii=False, indent=2))

    @app.command("run-final-audit")
    def run_final_audit_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        run_demo_scenarios: bool = typer.Option(False, "--run-demo-scenarios"),
    ) -> None:
        setup_logging()
        svc = ReleaseService(AppConfig.from_env())
        rep = svc.run_readiness_audit(profile_id)
        p = svc.save_readiness_report(rep.model_dump())
        extra = {"readiness_saved": str(p)}
        if run_demo_scenarios:
            pid = profile_id or svc.active_profile_id()
            prof = svc.get_release_profile(pid)
            results = []
            for sid in prof.get("demo_scenario_ids") or ["text_core_demo"]:
                try:
                    r = svc.run_demo_scenario(
                        sid,
                        profile_id=pid,
                        snapshot_id="dev_snapshot_v2",
                        topic_id="tc-campus-ai",
                    )
                    results.append(r.model_dump())
                except Exception as e:
                    results.append({"scenario_id": sid, "error": str(e)})
            extra["demo_results"] = results
        typer.echo(json.dumps({"readiness": rep.model_dump(), **extra}, ensure_ascii=False, indent=2))
        raise typer.Exit(0 if rep.overall_status != "blocked" else 1)
