"""acceptance_evidence_case — RC/readiness/stability/demo summarized in acceptance."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.application.handover_service import HandoverService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_acceptance_evidence_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected or {}
    pid = case.inputs.get("profile_id") or profile_id
    cfg = get_app_config()
    svc = HandoverService(cfg)
    ev = svc.build_acceptance_evidence(pid)["evidence"]
    ok = bool(ev.get("release_id") or ev.get("profile_id"))
    if exp.get("require_known_limitations_preserved"):
        lim = ev.get("accepted_limitations") or []
        ok = ok and isinstance(lim, list)
    if exp.get("require_summary_keys"):
        s = ev.get("summary") or {}
        ok = ok and all(k in s for k in exp["require_summary_keys"])
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={
            "passed_checks": len(ev.get("passed_checks") or []),
            "failed_checks": len(ev.get("failed_checks") or []),
        },
        metadata={"profile_id": pid},
    )
