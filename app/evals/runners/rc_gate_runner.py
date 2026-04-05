"""rc_gate_case."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.application.stability_service import StabilityService


def run_rc_gate_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    pid = case.inputs.get("profile_id") or profile_id
    cfg = get_app_config()
    svc = StabilityService(cfg)
    rep = svc.build_rc_report(pid)
    g = rep.get("go_no_go")
    allowed = exp.get("allowed_go") or ["go", "conditional_go", "no_go"]
    ok = g in allowed
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"go_no_go": g},
        metadata={"profile_id": profile_id},
    )
