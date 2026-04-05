"""release_manifest_case — final manifest aggregates release/stability refs."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.application.handover_service import HandoverService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_release_manifest_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected or {}
    pid = case.inputs.get("profile_id") or profile_id
    cfg = get_app_config()
    svc = HandoverService(cfg)
    out = svc.build_release_manifest(pid)
    m = out.get("manifest") or {}
    required = exp.get("required_manifest_refs") or ["profile_id", "included_artifact_refs", "release_id"]
    ok = all(k in m and m.get(k) is not None for k in required)
    if exp.get("required_profile_id"):
        ok = ok and m.get("profile_id") == exp["required_profile_id"]
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"manifest_keys": list(m.keys())[:20]},
        metadata={"profile_id": pid},
    )
