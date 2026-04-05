"""Final delivery / handover orchestration."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.release_service import ReleaseService
from app.application.stability_service import StabilityService
from app.handover.engines.acceptance_builder import build_acceptance_evidence
from app.handover.engines.bom_builder import build_bom
from app.handover.engines.demo_kit_builder import build_demo_kit
from app.handover.engines.delivery_verifier import verify_delivery
from app.handover.engines.docs_bundle_builder import export_docs_bundle
from app.handover.engines.handover_assembler import assemble_handover_kit
from app.handover.engines.manifest_builder import build_release_manifest
from app.handover.engines.runbook_builder import build_runbook_markdown
from app.ops.settings import get_ops_settings


class HandoverService:
    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or get_app_config()
        self._ops = get_ops_settings()
        self._release = ReleaseService(self._config)
        self._stability = StabilityService(self._config)

    def _profile(self, profile_id: str | None) -> str:
        return profile_id or getattr(self._ops, "default_final_release_profile", None) or getattr(
            self._ops, "active_release_profile", "v1_demo"
        )

    def build_release_manifest(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = self._profile(profile_id)
        m = build_release_manifest(
            pid,
            release_svc=self._release,
            stability_svc=self._stability,
            cfg=self._config,
            ops=self._ops,
        )
        d = Path(getattr(self._ops, "release_manifest_dir"))
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{pid}_release_manifest.json"
        p.write_text(json.dumps(m.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"manifest": m.model_dump(), "path": str(p)}

    def build_bom(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = self._profile(profile_id)
        b = build_bom(pid)
        d = Path(getattr(self._ops, "bom_dir"))
        d.mkdir(parents=True, exist_ok=True)
        jp = d / f"{pid}_bom.json"
        jp.write_text(json.dumps(b.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_lines = [f"# BOM ({pid})", "", f"- items: {len(b.entries)}", f"- warnings: {len(b.warnings)}", ""]
        for w in b.warnings[:20]:
            md_lines.append(f"- WARN: {w}")
        (d / f"{pid}_bom.md").write_text("\n".join(md_lines), encoding="utf-8")
        return {"bom": b.model_dump(), "json_path": str(jp)}

    def build_demo_kit(self, profile_id: str | None, output_dir: Path) -> dict[str, Any]:
        pid = self._profile(profile_id)
        man = build_demo_kit(
            pid,
            output_dir,
            release_export_demo_bundle=self._release.export_demo_bundle,
            run_demo_scenario_fn=self._release.run_demo_scenario,
            snapshot_id="dev_snapshot_v2",
            topic_id="tc-campus-ai",
        )
        mp = output_dir / "demo_kit_manifest.json"
        mp.write_text(json.dumps(man.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"manifest": man.model_dump(), "output_dir": str(output_dir.resolve())}

    def build_acceptance_evidence(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = self._profile(profile_id)
        ev = build_acceptance_evidence(pid, release_svc=self._release, stability_svc=self._stability, cfg=self._config, ops=self._ops)
        d = Path(getattr(self._ops, "acceptance_evidence_dir"))
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{pid}_acceptance_evidence.json"
        p.write_text(json.dumps(ev.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"evidence": ev.model_dump(), "path": str(p)}

    def verify_delivery(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = self._profile(profile_id)
        req = getattr(self._ops, "require_rc_go_or_conditional_go_for_handover", False)
        rep = verify_delivery(pid, snapshot_root=Path(self._config.snapshot_root), require_rc=req)
        vd = Path(getattr(self._ops, "delivery_verification_dir"))
        vd.mkdir(parents=True, exist_ok=True)
        vp = vd / f"{pid}_verification.json"
        vp.write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return rep.model_dump()

    def export_acceptance_markdown(self, profile_id: str | None, output_file: Path) -> Path:
        ev = build_acceptance_evidence(
            self._profile(profile_id), release_svc=self._release, stability_svc=self._stability, cfg=self._config, ops=self._ops
        )
        lines = [
            f"# Acceptance evidence ({ev.profile_id})",
            "",
            f"- readiness: {ev.summary.get('readiness_status')}",
            f"- RC: {ev.summary.get('rc_go_no_go')}",
            f"- stability: {ev.summary.get('stability_overall')}",
            "",
            "## Accepted limitations",
            *[f"- {x}" for x in ev.accepted_limitations],
            "",
            "## Passed checks",
            *[f"- {c}" for c in ev.passed_checks],
            "",
            "## Failed checks",
            *[f"- {c}" for c in ev.failed_checks],
            "",
        ]
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(lines), encoding="utf-8")
        return output_file

    def export_release_docs_bundle(self, profile_id: str | None, output_dir: Path) -> dict[str, Any]:
        pid = self._profile(profile_id)
        copied = export_docs_bundle(output_dir, profile_id=pid)
        (output_dir / "RUNBOOK.md").write_text(build_runbook_markdown(pid), encoding="utf-8")
        copied.append("RUNBOOK.md")
        return {"copied": copied, "output_dir": str(output_dir.resolve())}

    def build_handover_kit(self, profile_id: str | None, output_dir: Path) -> dict[str, Any]:
        pid = self._profile(profile_id)
        mf = self.build_release_manifest(pid)
        bom = self.build_bom(pid)
        acc = self.build_acceptance_evidence(pid)
        ver = self.verify_delivery(pid)
        demo_out = Path(getattr(self._ops, "demo_kit_dir")) / pid / "demo_kit_build"
        demo_out.mkdir(parents=True, exist_ok=True)
        demo = self.build_demo_kit(pid, demo_out)
        docs_out = Path(getattr(self._ops, "final_docs_bundle_dir")) / pid / "docs_bundle"
        docs = self.export_release_docs_bundle(pid, docs_out)
        mp = Path(mf["path"])
        bp = Path(bom["json_path"])
        ap = Path(acc["path"])
        vp = Path(getattr(self._ops, "delivery_verification_dir")) / f"{pid}_verification.json"

        hm = assemble_handover_kit(
            output_dir,
            profile_id=pid,
            manifest_path=mp,
            bom_path=bp,
            demo_kit_path=demo_out,
            acceptance_path=ap,
            verification_path=vp,
            docs_bundle_paths=docs.get("copied") or [],
        )
        return {"handover_manifest": hm.model_dump(), "output_dir": str(output_dir.resolve())}

    def package_final_release(self, profile_id: str | None, output_file: Path) -> dict[str, Any]:
        pid = self._profile(profile_id)
        if getattr(self._ops, "require_acceptance_evidence_before_package", False):
            self.build_acceptance_evidence(pid)
        kit_dir = Path(getattr(self._ops, "handover_kit_dir")) / pid / "kit"
        self.build_handover_kit(pid, kit_dir)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        base = output_file.with_suffix("") if output_file.suffix == ".zip" else output_file
        shutil.make_archive(str(base), "zip", root_dir=kit_dir)
        z = Path(str(base) + ".zip")
        pk = Path(getattr(self._ops, "final_release_dir"))
        pk.mkdir(parents=True, exist_ok=True)
        return {"zip_path": str(z.resolve()), "profile_id": pid}

    def list_release_manifests(self) -> list[str]:
        d = Path(getattr(self._ops, "release_manifest_dir"))
        if not d.is_dir():
            return []
        return sorted(x.name for x in d.glob("*_release_manifest.json"))

    def list_demo_kits(self) -> list[str]:
        d = Path(getattr(self._ops, "demo_kit_dir"))
        if not d.is_dir():
            return []
        return sorted(x.name for x in d.iterdir() if x.is_dir())

    def get_demo_kit_manifest_public(self, profile_id: str | None = None) -> dict[str, Any] | None:
        pid = self._profile(profile_id)
        p = Path(self._ops.demo_kit_dir) / pid / "demo_kit_build" / "demo_kit_manifest.json"
        if not p.is_file():
            return None
        return json.loads(p.read_text(encoding="utf-8"))

    def get_handover_kit_manifest_public(self, profile_id: str | None = None) -> dict[str, Any] | None:
        pid = self._profile(profile_id)
        p = Path(self._ops.handover_kit_dir) / pid / "kit" / "handover_kit_manifest.json"
        if not p.is_file():
            return None
        return json.loads(p.read_text(encoding="utf-8"))

    def get_handover_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        pid = self._profile(profile_id)
        rc = self._stability.build_rc_report(pid)
        readiness = self._release.run_readiness_audit(pid).model_dump()
        stab = self._stability.get_stability_report(pid, include_e2e=False)
        acc = build_acceptance_evidence(pid, release_svc=self._release, stability_svc=self._stability, cfg=self._config, ops=self._ops)
        issues = self._stability.list_known_issues()
        return {
            "profile_id": pid,
            "rc_go_no_go": rc.get("go_no_go"),
            "readiness_status": readiness.get("overall_status"),
            "stability_overall": stab.get("overall_status"),
            "acceptance_failed": len(acc.failed_checks),
            "acceptance_passed": len(acc.passed_checks),
            "known_issues_count": len(issues),
            "accepted_limitations_count": len(acc.accepted_limitations),
            "docs_bundle_enabled": getattr(self._ops, "enable_final_delivery_ui", True),
        }

    def run_final_demo(self, profile_id: str | None, snapshot_id: str, provider_name: str = "mock") -> dict[str, Any]:
        pid = self._profile(profile_id)
        r = self._release.run_demo_scenario(
            "text_core_demo",
            profile_id=pid,
            snapshot_id=snapshot_id,
            topic_id="tc-campus-ai",
            provider_name=provider_name,
        )
        return {"demo": r.model_dump(), "profile_id": pid}
