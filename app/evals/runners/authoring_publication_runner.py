"""authoring_publication_case — publication record fields."""

from __future__ import annotations

from pathlib import Path

from app.authoring.schemas.publication import PublicationRecord
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_publication_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    raw = case.inputs.get("publication") or {}
    rec = PublicationRecord.model_validate(raw)
    ok = bool(rec.publication_id and rec.output_ref and rec.published_version)
    if exp.get("required_publication_fields"):
        for f in exp["required_publication_fields"]:
            ok = ok and getattr(rec, f, None) is not None
    if exp.get("require_no_builtin_overwrite"):
        ok = ok and "builtin" not in (rec.output_ref or "").lower()
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"artifact_id": rec.artifact_id},
        metadata={"profile_id": profile_id},
    )
