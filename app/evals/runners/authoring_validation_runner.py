"""authoring_validation_case — draft lint + validation."""

from __future__ import annotations

from pathlib import Path

from app.authoring.engines.validator import run_validation
from app.authoring.schemas.draft import AuthoringDraft
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_authoring_validation_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    raw = inp.get("draft") or {}
    draft = AuthoringDraft.model_validate(raw)
    rep = run_validation(draft)
    ok = rep.valid
    if exp.get("min_findings") is not None:
        ok = ok and len(rep.findings) >= int(exp["min_findings"])
    if exp.get("require_error_rule"):
        ok = ok and any(f.get("rule_id") == exp["require_error_rule"] for f in rep.findings)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"valid": rep.valid, "finding_count": len(rep.findings)},
        metadata={"profile_id": profile_id},
    )
