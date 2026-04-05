"""Stability / E2E / RC CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.release_service import ReleaseService
from app.application.stability_service import StabilityService
from app.logging import setup_logging

def register_stability_cli(app: typer.Typer) -> None:
    @app.command("list-e2e-scenarios")
    def list_e2e_scenarios_cmd() -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_e2e_scenarios(), ensure_ascii=False, indent=2))

    @app.command("show-e2e-scenario")
    def show_e2e_scenario_cmd(scenario_id: str = typer.Option(..., "--scenario-id")) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        spec = svc.get_e2e_scenario(scenario_id)
        if not spec:
            typer.echo("scenario not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(spec, ensure_ascii=False, indent=2))

    @app.command("run-e2e-scenario")
    def run_e2e_scenario_cmd(
        scenario_id: str = typer.Option(..., "--scenario-id"),
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        snapshot_id: str = typer.Option("dev_snapshot_v2", "--snapshot-id"),
        topic_id: str = typer.Option("tc-campus-ai", "--topic-id"),
        provider: str = typer.Option("mock", "--provider"),
    ) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        r = svc.run_e2e_scenario(
            scenario_id,
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider,
        )
        typer.echo(json.dumps(r.model_dump(), ensure_ascii=False, indent=2))
        raise typer.Exit(0 if r.success else 1)

    @app.command("run-e2e-matrix")
    def run_e2e_matrix_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        snapshot_id: str = typer.Option("dev_snapshot_v2", "--snapshot-id"),
        topic_id: str = typer.Option("tc-campus-ai", "--topic-id"),
        provider: str = typer.Option("mock", "--provider"),
    ) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        rows = svc.run_e2e_matrix(
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider,
        )
        typer.echo(json.dumps([r.model_dump() for r in rows], ensure_ascii=False, indent=2))
        ok = all(r.success for r in rows)
        raise typer.Exit(0 if ok else 1)

    @app.command("run-consistency-audit")
    def run_consistency_audit_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        row = svc.run_consistency_audit(profile_id)
        typer.echo(json.dumps(row, ensure_ascii=False, indent=2))

    @app.command("list-known-issues")
    def list_known_issues_cmd() -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        typer.echo(json.dumps(svc.list_known_issues(), ensure_ascii=False, indent=2))

    @app.command("show-stability-report")
    def show_stability_report_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        include_e2e: bool = typer.Option(False, "--include-e2e"),
    ) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        rep = svc.get_stability_report(profile_id, include_e2e=include_e2e)
        typer.echo(json.dumps(rep, ensure_ascii=False, indent=2))

    @app.command("build-rc-report")
    def build_rc_report_cmd(profile_id: Optional[str] = typer.Option(None, "--profile-id")) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        rep = svc.build_rc_report(profile_id)
        typer.echo(json.dumps(rep, ensure_ascii=False, indent=2))

    @app.command("export-known-limitations")
    def export_known_limitations_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        output_file: Path = typer.Option(..., "--output-file", "-o"),
    ) -> None:
        setup_logging()
        svc = StabilityService(AppConfig.from_env())
        p = svc.export_known_limitations_file(profile_id, output_file)
        typer.echo(json.dumps({"written": str(p)}, ensure_ascii=False, indent=2))

    @app.command("run-final-regression")
    def run_final_regression_cmd(
        profile_id: Optional[str] = typer.Option(None, "--profile-id"),
        run_readiness: bool = typer.Option(True, "--run-readiness/--no-run-readiness"),
        run_consistency: bool = typer.Option(True, "--run-consistency/--no-run-consistency"),
        run_e2e: bool = typer.Option(True, "--run-e2e/--no-run-e2e"),
        snapshot_id: str = typer.Option("dev_snapshot_v2", "--snapshot-id"),
        topic_id: str = typer.Option("tc-campus-ai", "--topic-id"),
    ) -> None:
        setup_logging()
        cfg = AppConfig.from_env()
        out: dict = {}
        if run_readiness:
            rsvc = ReleaseService(cfg)
            out["readiness"] = rsvc.run_readiness_audit(profile_id).model_dump()
        if run_consistency:
            svc = StabilityService(cfg)
            out["consistency"] = svc.run_consistency_audit(profile_id)
        if run_e2e:
            svc = StabilityService(cfg)
            rows = svc.run_e2e_matrix(profile_id=profile_id, snapshot_id=snapshot_id, topic_id=topic_id)
            out["e2e"] = [r.model_dump() for r in rows]
        svc = StabilityService(cfg)
        out["stability_report"] = svc.get_stability_report(profile_id, include_e2e=False)
        out["rc_report"] = svc.build_rc_report(profile_id)
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))
        rc = out.get("rc_report") or {}
        g = rc.get("go_no_go", "no_go")
        raise typer.Exit(0 if g in ("go", "conditional_go") else 1)
