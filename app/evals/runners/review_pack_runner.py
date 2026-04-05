"""review_pack_case — verify pack aggregates expected artifact keys."""

from __future__ import annotations

import json
from pathlib import Path

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_review_pack_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    pack_path = resolve_path(str(inp["review_pack_fixture"]))
    raw = json.loads(Path(pack_path).read_text(encoding="utf-8"))
    inc = raw.get("included_artifacts") or {}
    ok = True
    for key in exp.get("required_artifact_keys", []):
        if key not in inc:
            ok = False
    rd = (raw.get("ai_summary") or {}).get("rubric_dimensions")
    if exp.get("required_rubric_dimensions"):
        n = len(rd or [])
        ok = ok and n >= int(exp["required_rubric_dimensions"].get("min_count", 0))
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"included_keys": list(inc.keys())},
        metadata={"profile_id": profile_id, "snapshot_dir": str(snapshot_dir)},
    )
