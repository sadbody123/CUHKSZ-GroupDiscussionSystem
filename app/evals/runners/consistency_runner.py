"""consistency_case."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.stability.engines.consistency_auditor import run_consistency_audit


def run_consistency_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    pid = case.inputs.get("profile_id") or "v1_demo"
    _, summary = run_consistency_audit(pid)
    ok = summary.get("finding_count", 0) >= exp.get("min_findings", 0)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details=summary,
        metadata={"profile_id": profile_id},
    )
