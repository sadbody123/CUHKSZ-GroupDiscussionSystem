"""launch_bridge_case — step maps to session kwargs."""

from __future__ import annotations

from pathlib import Path

from app.curriculum.engines.launch_bridge import build_session_launch_kwargs
from app.curriculum.loaders.yaml_loader import load_builtin_pack
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_launch_bridge_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    pack_id = str(inp.get("pack_id", "foundation_gd_pack"))
    step_id = str(inp.get("step_id", "step_foundation_01"))
    pk = load_builtin_pack(pack_id)
    if not pk:
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=False,
            score=0.0,
            details={"error": "pack missing"},
            metadata={},
        )
    kwargs = build_session_launch_kwargs(
        pk,
        step_id,
        learner_id="eval_learner",
        snapshot_id="dev_snapshot_v2",
    )
    ok = "snapshot_id" in kwargs and kwargs.get("topic_id")
    if exp.get("required_keys"):
        for k in exp["required_keys"]:
            ok = ok and k in kwargs
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=bool(ok),
        score=1.0 if ok else 0.0,
        details={"keys": list(kwargs.keys())},
        metadata={},
    )
