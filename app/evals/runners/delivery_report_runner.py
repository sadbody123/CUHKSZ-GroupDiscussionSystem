"""delivery_report_case — assignment report contains required fields."""

from __future__ import annotations

from pathlib import Path

from app.curriculum.engines.assignment_planner import plan_assignment_from_pack
from app.curriculum.engines.delivery_analytics import build_assignment_report
from app.curriculum.loaders.yaml_loader import load_builtin_pack
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_delivery_report_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
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
    rep = build_assignment_report(spec, {"pack_id": pk.pack_id, "display_name": pk.display_name})
    ok = bool(rep.report_id and rep.assignment_id)
    if exp.get("required_report_fields"):
        dumped = rep.model_dump()
        for f in exp["required_report_fields"]:
            ok = ok and f in dumped and dumped[f] is not None
    if exp.get("require_proxy_notes_preserved"):
        ok = ok and len(rep.proxy_notes) > 0
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"report_id": rep.report_id},
        metadata={},
    )
