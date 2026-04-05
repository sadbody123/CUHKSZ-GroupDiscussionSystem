"""override_merge_case — approved overrides produce reviewed artifact with audit fields."""

from __future__ import annotations

import json
from pathlib import Path

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.review.engines.override_merger import merge_reviewed_feedback
from app.review.schemas.override import OverrideDecision


def run_override_merge_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    coach_path = resolve_path(str(inp["coach_report_fixture"]))
    coach = json.loads(Path(coach_path).read_text(encoding="utf-8"))
    ovs_raw = json.loads(Path(resolve_path(str(inp["overrides_fixture"]))).read_text(encoding="utf-8"))
    ods = [OverrideDecision.model_validate(x) for x in ovs_raw]
    art = merge_reviewed_feedback(
        base_coach_report=coach,
        overrides=ods,
        review_id="eval_r1",
        reviewer_id="eval_rev",
        review_pack_id="eval_pack",
        session_id="eval_sess",
    )
    ok = bool(art.review_id and art.reviewer_id and art.proxy_note)
    if exp.get("require_payload_keys"):
        for k in exp["require_payload_keys"]:
            ok = ok and k in art.payload
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"artifact_kind": art.artifact_kind},
        metadata={},
    )
