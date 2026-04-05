"""delivery_verification_case — quickstart verifier outcomes."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.handover.engines.delivery_verifier import verify_delivery
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_delivery_verification_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected or {}
    pid = case.inputs.get("profile_id") or profile_id
    cfg = get_app_config()
    rep = verify_delivery(pid, snapshot_root=Path(cfg.snapshot_root), require_rc=False)
    allowed = exp.get("allowed_overall_status") or ["ok", "warning"]
    ok = rep.overall_status in allowed
    if exp.get("require_blocked_if_missing_docs") and rep.overall_status == "blocked":
        ok = exp.get("accept_blocked", False)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"overall_status": rep.overall_status, "failed_steps": rep.failed_steps},
        metadata={"profile_id": pid},
    )
