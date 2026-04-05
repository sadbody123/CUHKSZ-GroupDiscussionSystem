"""disagreement_case — mismatch categories present in analysis."""

from __future__ import annotations

import json
from pathlib import Path

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.review.engines.disagreement_analyzer import analyze_strength_risk_overlap


def run_disagreement_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    raw = json.loads(Path(resolve_path(str(inp["disagreement_fixture"]))).read_text(encoding="utf-8"))
    disc = analyze_strength_risk_overlap(
        raw.get("ai_strengths", []),
        raw.get("ai_risks", []),
        raw.get("human_notes", []),
    )
    ok = True
    for mt in exp.get("required_mismatch_types", []):
        ok = ok and bool(disc.get(mt))
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details=disc,
        metadata={},
    )
