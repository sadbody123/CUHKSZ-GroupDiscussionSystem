"""scope_freeze_case — freeze summary."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.release.engines.scope_freezer import build_scope_freeze_summary


def run_scope_freeze_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    pid = case.inputs.get("profile_id") or "v1_demo"
    s = build_scope_freeze_summary(pid)
    ok = bool(s.summary_text and s.decisions)
    if exp.get("required_report_fields"):
        dumped = s.model_dump()
        for f in exp["required_report_fields"]:
            ok = ok and f in dumped
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"decision_count": len(s.decisions)},
        metadata={"profile_id": profile_id},
    )
