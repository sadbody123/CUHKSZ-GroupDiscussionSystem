"""Release / capability / demo orchestration."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.ops.settings import get_ops_settings
from app.release.engines.bundle_builder import build_demo_bundle
from app.release.engines.capability_registry import all_capabilities
from app.release.engines.readiness_audit import run_readiness_audit as run_readiness_audit_engine
from app.release.engines.scenario_runner import run_demo_scenario as engine_run_scenario
from app.release.engines.scope_freezer import build_scope_freeze_summary
from app.release.loaders.profile_loader import list_profile_ids, load_release_profile
from app.release.pipeline.build_capability_matrix import build_capability_matrix_json


class ReleaseService:
    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or get_app_config()
        self._ops = get_ops_settings()

    def active_profile_id(self) -> str:
        return getattr(self._ops, "active_release_profile", None) or "v1_demo"

    def list_capabilities(self) -> list[dict[str, Any]]:
        return [c.model_dump() for c in all_capabilities()]

    def get_capability_matrix(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or self.active_profile_id()
        return build_capability_matrix_json(pid)

    def list_release_profiles(self) -> list[str]:
        return list_profile_ids()

    def get_release_profile(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or self.active_profile_id()
        return load_release_profile(pid).model_dump()

    def run_readiness_audit(self, profile_id: str | None = None):
        pid = profile_id or self.active_profile_id()
        return run_readiness_audit_engine(pid, cfg=self._config)

    def run_demo_scenario(
        self,
        scenario_id: str,
        *,
        profile_id: str | None = None,
        snapshot_id: str,
        topic_id: str,
        provider_name: str = "mock",
    ):
        pid = profile_id or self.active_profile_id()
        if getattr(self._ops, "require_readiness_before_api_demo", False):
            rep = run_readiness_audit_engine(pid, cfg=self._config)
            if rep.overall_status == "blocked":
                raise ValueError("readiness blocked")
        return engine_run_scenario(
            scenario_id,
            profile_id=pid,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
            cfg=self._config,
        )

    def export_demo_bundle(
        self,
        profile_id: str | None,
        output_dir: Path,
        *,
        run_scenarios: list[str] | None = None,
    ) -> dict[str, Any]:
        pid = profile_id or self.active_profile_id()
        rep = run_readiness_audit_engine(pid, cfg=self._config).model_dump()
        prof = load_release_profile(pid)
        results: list[dict[str, Any]] = []
        for sid in run_scenarios or prof.demo_scenario_ids or ["text_core_demo"]:
            try:
                r = engine_run_scenario(
                    sid,
                    profile_id=pid,
                    snapshot_id="dev_snapshot_v2",
                    topic_id="tc-campus-ai",
                    provider_name="mock",
                    cfg=self._config,
                )
                results.append(r.model_dump())
            except Exception as e:
                results.append({"scenario_id": sid, "error": str(e)})
        scope = build_scope_freeze_summary(pid).model_dump()
        man = build_demo_bundle(
            profile_id=pid,
            output_dir=output_dir,
            readiness_report=rep,
            scenario_results=results,
            scope_summary=scope,
        )
        return {"manifest": man.model_dump(), "output_dir": str(output_dir.resolve())}

    def get_scope_freeze_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or self.active_profile_id()
        return build_scope_freeze_summary(pid).model_dump()

    def get_release_visibility_state(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = profile_id or self.active_profile_id()
        prof = load_release_profile(pid)
        return {
            "profile_id": prof.profile_id,
            "ui_visibility_policy": prof.ui_visibility_policy,
            "api_visibility_policy": prof.api_visibility_policy,
            "gating_enabled": getattr(self._ops, "enable_release_gating", True),
        }

    def save_readiness_report(self, report: dict[str, Any]) -> Path:
        d = Path(getattr(self._ops, "release_report_dir", Path("storage/release/reports")))
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"readiness_{report.get('profile_id', 'unknown')}_{uuid.uuid4().hex[:8]}.json"
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p
