"""demo_scenario_case — run canonical demo via scenario_runner."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.release.engines.scenario_runner import run_demo_scenario


def run_demo_scenario_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected
    sid = case.inputs.get("scenario_id") or "text_core_demo"
    pid = case.inputs.get("profile_id") or profile_id
    snap_id = case.snapshot_id or case.inputs.get("snapshot_id") or snapshot_dir.name
    topic = case.topic_id or case.inputs.get("topic_id") or "tc-campus-ai"
    provider = case.inputs.get("provider_name") or "mock"
    cfg = get_app_config()
    r = run_demo_scenario(
        sid,
        profile_id=pid,
        snapshot_id=snap_id,
        topic_id=topic,
        provider_name=provider,
        cfg=cfg,
    )
    ok = bool(r.result_id and r.scenario_id)
    if exp.get("require_success"):
        ok = ok and r.success
    if exp.get("require_step_keys"):
        keys = {s.get("step") for s in r.step_results}
        ok = ok and all(k in keys for k in exp["require_step_keys"])
    if exp.get("require_experimental_note_preserved"):
        ok = ok and isinstance(r.metadata, dict)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"scenario_id": r.scenario_id, "success": r.success},
        metadata={"profile_id": profile_id},
    )
