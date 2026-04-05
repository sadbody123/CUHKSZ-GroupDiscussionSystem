"""assignment_progress_case — assignment spec step refs and status transitions."""

from __future__ import annotations

from pathlib import Path

from app.curriculum.engines.assignment_planner import plan_assignment_from_pack
from app.curriculum.loaders.yaml_loader import load_builtin_pack
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_assignment_progress_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    pk = load_builtin_pack("foundation_gd_pack")
    if not pk:
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=False,
            score=0.0,
            details={},
            metadata={},
        )
    spec = plan_assignment_from_pack(
        pk,
        learner_ids=["eval_learner"],
        title="eval",
        created_by="eval",
        activate=True,
    )
    ok = spec.status == "active" and len(spec.step_refs) == len(pk.steps)
    if exp.get("required_status"):
        ok = ok and spec.status == exp["required_status"]
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"total_steps": spec.total_steps, "ref_count": len(spec.step_refs)},
        metadata={},
    )
