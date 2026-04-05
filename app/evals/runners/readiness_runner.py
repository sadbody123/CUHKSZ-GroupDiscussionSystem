"""readiness_case — audit structure."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.release.engines.readiness_audit import run_readiness_audit


def run_readiness_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    pid = case.inputs.get("profile_id") or "v1_demo"
    rep = run_readiness_audit(pid)
    allowed = exp.get("allowed_statuses") or ["ready", "warning"]
    ok = rep.overall_status in allowed
    if exp.get("required_check_categories"):
        cats = {c.get("category") for c in rep.checks}
        ok = ok and all(x in cats for x in exp["required_check_categories"])
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"overall_status": rep.overall_status},
        metadata={"profile_id": profile_id},
    )
