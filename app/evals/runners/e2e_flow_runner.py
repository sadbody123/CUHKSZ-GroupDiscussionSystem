"""e2e_flow_case."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.stability.engines.scenario_orchestrator import run_e2e_scenario


def run_e2e_flow_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    sid = case.inputs.get("scenario_id") or "text_core_cli"
    pid = case.inputs.get("profile_id") or profile_id
    snap = case.snapshot_id or case.inputs.get("snapshot_id") or snapshot_dir.name
    topic = case.topic_id or case.inputs.get("topic_id") or "tc-campus-ai"
    cfg = get_app_config()
    r = run_e2e_scenario(
        sid,
        profile_id=pid,
        snapshot_id=snap,
        topic_id=topic,
        provider_name=case.inputs.get("provider_name") or "mock",
        cfg=cfg,
    )
    d = r.model_dump()
    ok = all(k in d for k in exp.get("required_fields", ["run_id", "success"]))
    if exp.get("require_success"):
        ok = ok and r.success
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"scenario_id": sid, "success": r.success},
        metadata={"profile_id": profile_id},
    )
