"""patch_proposal_case — patch proposal shape."""

from __future__ import annotations

from pathlib import Path

from app.authoring.schemas.patch import PatchProposal
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_patch_proposal_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:  # noqa: N802
    exp = case.expected
    raw = case.inputs.get("patch") or {}
    p = PatchProposal.model_validate(raw)
    ok = bool(p.reason and p.evidence_refs and p.proposed_ops)
    if exp.get("required_target_type"):
        ok = ok and p.target_artifact_type == exp["required_target_type"]
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"patch_id": p.patch_id},
        metadata={"profile_id": profile_id},
    )
