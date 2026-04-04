"""e2e_case runner using application services (mock)."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_e2e_case(case: EvalCase, snapshot_dir: Path, profile_id: str, tmp_session_root: Path) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    cfg = get_app_config().model_copy(update={"session_storage_dir": tmp_session_root})
    snap_name = snapshot_dir.name
    svc = SessionService(cfg)
    ctx = svc.create_session(
        snapshot_id=snap_name,
        topic_id=str(inp["topic_id"]),
        user_stance=inp.get("user_stance"),
        provider_name=str(inp.get("provider_name", "mock")),
        runtime_profile_id=profile_id or case.runtime_profile_id,
        source="eval",
    )
    disc = DiscussionService(cfg, svc)
    fb = FeedbackService(svc)
    disc.submit_user_turn(ctx.session_id, str(inp.get("initial_user_turn", "Hello e2e.")))
    steps = int(inp.get("auto_steps", 2))
    disc.auto_run_discussion(ctx.session_id, max_steps=steps, auto_fill_user=True)
    report = fb.generate_feedback(ctx.session_id)
    sess = svc.get_session(ctx.session_id)
    ok = True
    if exp.get("min_turn_count") is not None:
        ok = ok and len(sess.turns) >= int(exp["min_turn_count"])
    if exp.get("feedback_generated"):
        ok = ok and sess.coach_report is not None
    if exp.get("final_phase_in"):
        ok = ok and sess.phase in exp["final_phase_in"]
    for s in exp.get("report_contains_any", []) or []:
        ok = ok and s.lower() in (report.text or "").lower()
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"turns": len(sess.turns), "phase": sess.phase},
        metadata={"session_id": ctx.session_id},
    )
