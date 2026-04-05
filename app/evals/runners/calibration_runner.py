"""calibration_case — agreement level matches expected band."""

from __future__ import annotations

import json
from pathlib import Path

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.review.engines.calibration_engine import build_calibration_report
from app.review.schemas.report import HumanReview


def run_calibration_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    coach = json.loads(Path(resolve_path(str(inp["coach_fixture"]))).read_text(encoding="utf-8"))
    hr_raw = json.loads(Path(resolve_path(str(inp["human_review_fixture"]))).read_text(encoding="utf-8"))
    hr = HumanReview.model_validate(hr_raw)
    rep = build_calibration_report(
        review_pack_id="eval_pack",
        session_id="eval_sess",
        review_id=hr.review_id,
        coach_report=coach,
        human=hr,
    )
    allowed = exp.get("expected_agreement_levels") or (
        [exp["expected_agreement_level"]] if exp.get("expected_agreement_level") else None
    )
    ok = rep.overall_agreement in allowed if allowed else True
    if exp.get("require_proxy_notes_preserved"):
        ok = ok and bool(rep.metadata.get("disagreement_analysis"))
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"overall_agreement": rep.overall_agreement},
        metadata={},
    )
