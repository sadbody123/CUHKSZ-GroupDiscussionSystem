"""recovery_policy_case."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.stability.engines.recovery_policy import recovery_policy_summary


def run_recovery_policy_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    s = recovery_policy_summary()
    pol = s.get("policies") or []
    ok = len(pol) >= exp.get("min_policies", 1)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"policy_count": len(pol)},
        metadata={"profile_id": profile_id},
    )
