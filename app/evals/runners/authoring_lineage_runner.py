"""authoring_lineage_case — derivative chain tracking."""

from __future__ import annotations

from pathlib import Path

from app.authoring.engines.diff_builder import build_diff
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_lineage_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    base = case.inputs.get("base_content") or {}
    draft = case.inputs.get("draft_content") or {}
    changes = build_diff(base, draft)
    ok = len(changes) > 0
    if exp.get("required_lineage_refs"):
        blob = str(case.inputs.get("metadata") or {})
        for ref in exp["required_lineage_refs"]:
            ok = ok and ref in blob
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"change_count": len(changes)},
        metadata={"profile_id": profile_id},
    )
