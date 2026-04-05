"""capability_matrix_case — profile vs matrix."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.release.engines.feature_gate import is_capability_enabled, load_profile_or_default
from app.release.pipeline.build_capability_matrix import build_capability_matrix_json


def run_capability_matrix_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    pid = case.inputs.get("profile_id") or "v1_demo"
    prof = load_profile_or_default(pid)
    mat = build_capability_matrix_json(pid)
    ok = len(mat.get("capabilities", [])) > 0
    if exp.get("required_enabled"):
        for cid in exp["required_enabled"]:
            ok = ok and is_capability_enabled(prof, cid)
    if exp.get("required_disabled"):
        for cid in exp["required_disabled"]:
            ok = ok and not is_capability_enabled(prof, cid)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"capability_count": len(mat.get("capabilities", []))},
        metadata={"profile_id": pid},
    )
