"""Stability / E2E / RC orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.release_service import ReleaseService
from app.ops.settings import get_ops_settings
from app.stability.engines.consistency_auditor import run_consistency_audit
from app.stability.engines.interface_consistency import build_interface_consistency_summary
from app.stability.engines.issue_registry import findings_to_issues, merge_issues
from app.stability.engines.known_limitations import accepted_limitation_lines, filter_known_issues_for_api
from app.stability.engines.rc_gate import build_rc_report, stability_overall_from_signals
from app.stability.engines.recovery_policy import recovery_policy_summary
from app.stability.engines.scenario_matrix import get_e2e_scenario, list_e2e_scenarios
from app.stability.engines.scenario_orchestrator import run_e2e_matrix, run_e2e_scenario
from app.stability.engines.stability_report_builder import build_stability_report
from app.stability.pipeline.export_known_issues import export_known_limitations_md
from app.stability.schemas.consistency import ConsistencyFinding
from app.stability.schemas.issue import IssueRecord
from app.stability.schemas.scenario import E2ERunResult
from app.stability.store.issue_store import load_issues_from_path


class StabilityService:
    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or get_app_config()
        self._ops = get_ops_settings()
        self._release = ReleaseService(self._config)

    def _e2e_dir(self) -> Path | None:
        d = getattr(self._ops, "e2e_scenario_dir", None)
        return Path(d).resolve() if d else None

    def _known_issues_paths(self) -> list[Path]:
        out: list[Path] = []
        kd = getattr(self._ops, "known_issues_dir", None)
        if kd:
            out.append(Path(kd) / "issues.yaml")
        root = Path(__file__).resolve().parents[2]
        out.append(root / "tests" / "fixtures" / "stability" / "known_issues" / "issues.yaml")
        return out

    def list_e2e_scenarios(self) -> list[dict[str, Any]]:
        return [s.model_dump() for s in list_e2e_scenarios(self._e2e_dir())]

    def get_e2e_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        spec = get_e2e_scenario(scenario_id, extra_dir=self._e2e_dir())
        return spec.model_dump() if spec else None

    def run_e2e_scenario(
        self,
        scenario_id: str,
        *,
        profile_id: str | None = None,
        snapshot_id: str,
        topic_id: str,
        provider_name: str = "mock",
    ) -> E2ERunResult:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        return run_e2e_scenario(
            scenario_id,
            profile_id=pid,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
            cfg=self._config,
            e2e_scenario_dir=self._e2e_dir(),
        )

    def run_e2e_matrix(
        self,
        *,
        profile_id: str | None = None,
        snapshot_id: str,
        topic_id: str,
        provider_name: str = "mock",
        scenario_ids: list[str] | None = None,
    ) -> list[E2ERunResult]:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        results = run_e2e_matrix(
            profile_id=pid,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
            cfg=self._config,
            scenario_ids=scenario_ids,
            e2e_scenario_dir=self._e2e_dir(),
        )
        self._persist_e2e_results(pid, results)
        return results

    def _persist_e2e_results(self, profile_id: str, results: list[E2ERunResult]) -> None:
        d = Path(getattr(self._ops, "e2e_results_dir", self._ops.stability_report_dir.parent / "e2e_results"))
        d.mkdir(parents=True, exist_ok=True)
        payload = {"profile_id": profile_id, "results": [r.model_dump() for r in results]}
        (d / "latest_e2e.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def run_consistency_audit(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        findings, summary = run_consistency_audit(pid, cfg=self._config)
        row = {"profile_id": pid, "summary": summary, "findings": [f.model_dump() for f in findings]}
        cd = Path(getattr(self._ops, "consistency_report_dir", self._ops.stability_report_dir.parent / "consistency"))
        cd.mkdir(parents=True, exist_ok=True)
        (cd / "latest_consistency.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return row

    def list_known_issues(self) -> list[dict[str, Any]]:
        manual: list[IssueRecord] = []
        for p in self._known_issues_paths():
            manual.extend(load_issues_from_path(p))
        findings, _ = run_consistency_audit(
            getattr(self._ops, "active_release_profile", "v1_demo"),
            cfg=self._config,
        )
        merged = merge_issues(manual, findings_to_issues(findings))
        return filter_known_issues_for_api(merged)

    def get_stability_report(
        self,
        profile_id: str | None = None,
        *,
        include_e2e: bool = False,
        snapshot_id: str = "dev_snapshot_v2",
        topic_id: str = "tc-campus-ai",
    ) -> dict[str, Any]:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        audit = self.run_consistency_audit(pid)
        findings_raw = audit["findings"]
        findings = [ConsistencyFinding.model_validate(x) for x in findings_raw]
        e2e_results: list[E2ERunResult] = []
        if include_e2e:
            e2e_results = self.run_e2e_matrix(
                profile_id=pid,
                snapshot_id=snapshot_id,
                topic_id=topic_id,
            )
        else:
            ed = Path(getattr(self._ops, "e2e_results_dir", Path(self._config.session_storage_dir).parent / "e2e_results"))
            latest = ed / "latest_e2e.json"
            if latest.is_file():
                raw = json.loads(latest.read_text(encoding="utf-8"))
                for r in raw.get("results", []) or []:
                    e2e_results.append(E2ERunResult.model_validate(r))
        issues_data = self.list_known_issues()
        issues = [IssueRecord.model_validate(x) for x in issues_data]
        lim_lines = accepted_limitation_lines(issues)
        rep = build_stability_report(
            profile_id=pid,
            findings=findings,
            e2e_results=e2e_results,
            issues=issues,
            known_limitation_lines=lim_lines,
        )
        sd = Path(getattr(self._ops, "stability_report_dir"))
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "latest_stability.json").write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return rep.model_dump()

    def build_rc_report(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        readiness = self._release.run_readiness_audit(pid)
        audit = self.run_consistency_audit(pid)
        findings = audit["findings"]
        errs = sum(1 for f in findings if not f.get("passed") and f.get("severity") == "error")
        e2e_results: list[E2ERunResult] = []
        el = Path(getattr(self._ops, "e2e_results_dir", Path(self._config.session_storage_dir).parent / "e2e_results")) / "latest_e2e.json"
        if el.is_file():
            raw = json.loads(el.read_text(encoding="utf-8"))
            for r in raw.get("results", []) or []:
                e2e_results.append(E2ERunResult.model_validate(r))
        e2e_ok = all(r.success for r in e2e_results) if e2e_results else True
        stab = stability_overall_from_signals(
            consistency_errors=errs,
            consistency_warnings=sum(1 for f in findings if not f.get("passed") and f.get("severity") == "warning"),
            e2e_failed=sum(1 for r in e2e_results if not r.success) if e2e_results else 0,
        )
        issues = [IssueRecord.model_validate(x) for x in self.list_known_issues()]
        rc = build_rc_report(
            profile_id=pid,
            readiness_status=readiness.overall_status,
            stability_overall=stab,
            open_issues=[i for i in issues if i.status == "open"],
            e2e_all_success=e2e_ok,
            consistency_failed_errors=errs,
        )
        rd = Path(getattr(self._ops, "rc_report_dir"))
        rd.mkdir(parents=True, exist_ok=True)
        (rd / "latest_rc.json").write_text(json.dumps(rc.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return rc.model_dump()

    def get_recovery_policy_summary(self) -> dict[str, object]:
        return recovery_policy_summary()

    def get_interface_consistency_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        return build_interface_consistency_summary(pid)

    def export_known_limitations_file(self, profile_id: str | None, output_file: Path) -> Path:
        pid = profile_id or getattr(self._ops, "active_release_profile", "v1_demo")
        rows = [IssueRecord.model_validate(x) for x in self.list_known_issues()]
        return export_known_limitations_md(rows, profile_id=pid, output_file=output_file)
