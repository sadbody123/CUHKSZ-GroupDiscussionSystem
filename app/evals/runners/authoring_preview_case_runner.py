"""authoring_preview_case — preview sandbox structure."""

from __future__ import annotations

from pathlib import Path

from app.application.config import AppConfig
from app.authoring.engines.preview_runner import run_preview
from app.authoring.schemas.draft import AuthoringDraft
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_preview_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    raw = case.inputs.get("draft") or {}
    draft = AuthoringDraft.model_validate(raw)
    cfg = AppConfig.from_env()
    kind = str(case.inputs.get("preview_kind") or "artifact_render")
    res = run_preview(
        cfg,
        draft,
        preview_kind=kind,
        snapshot_id=case.inputs.get("snapshot_id"),
        provider_name="mock",
        learner_id=case.inputs.get("learner_id"),
    )
    ok = res.success
    if exp.get("required_summary_keys"):
        for k in exp["required_summary_keys"]:
            ok = ok and k in (res.summary or {})
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"preview_kind": kind},
        metadata={"profile_id": profile_id},
    )
