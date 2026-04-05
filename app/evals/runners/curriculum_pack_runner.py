"""curriculum_pack_case — builtin pack loads and meets schema expectations."""

from __future__ import annotations

from pathlib import Path

from app.curriculum.loaders.yaml_loader import load_builtin_pack
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_curriculum_pack_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    pack_id = str(inp.get("pack_id", "foundation_gd_pack"))
    pk = load_builtin_pack(pack_id)
    if not pk:
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=False,
            score=0.0,
            details={"pack_id": pack_id, "error": "pack not found"},
            metadata={"profile_id": profile_id},
        )
    ok = True
    if exp.get("required_step_count") is not None:
        ok = ok and len(pk.steps) >= int(exp["required_step_count"])
    if exp.get("required_focus_skills"):
        sk = {x.lower() for x in (pk.target_skills or [])}
        for fs in exp["required_focus_skills"]:
            ok = ok and fs.lower() in sk
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"pack_id": pack_id, "step_count": len(pk.steps)},
        metadata={"profile_id": profile_id},
    )
