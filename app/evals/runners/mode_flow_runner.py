"""mode_flow_case — mode constraints and timer fields after a user turn."""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.application.config import get_app_config
from app.application.discussion_service import DiscussionService
from app.application.mode_service import ModeService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.modes.loaders.yaml_loader import get_mode_registry


def run_mode_flow_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    snapshot_id = str(inp.get("snapshot_id") or snapshot_dir.name)
    topic_id = str(inp.get("topic_id") or "tc-campus-ai")
    mode_id = str(inp.get("mode_id") or "micro_drill")
    drill_id = inp.get("drill_id")

    long_text = str(inp.get("user_text") or ("word " * 220))

    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        cfg = get_app_config().model_copy(
            update={
                "session_storage_dir": (tmp / "sessions").resolve(),
                "learner_storage_dir": (tmp / "learners").resolve(),
                "speech_report_dir": (tmp / "speech").resolve(),
                "mode_reports_dir": (tmp / "mode_reports").resolve(),
                "snapshot_root": snapshot_dir.parent.resolve(),
                "enable_practice_modes": True,
            }
        )
        for d in (tmp / "sessions", tmp / "learners", tmp / "speech", tmp / "mode_reports"):
            d.mkdir(parents=True, exist_ok=True)

        svc = SessionService(cfg)
        disc = DiscussionService(cfg, svc)
        msvc = ModeService(cfg, svc)
        ctx = svc.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance="neutral",
            provider_name="mock",
            runtime_profile_id=profile_id or inp.get("runtime_profile_id") or "default",
            mode_id=mode_id,
            drill_id=drill_id,
            source="eval",
        )
        disc.submit_user_turn(ctx.session_id, long_text)
        st = msvc.get_mode_status(ctx.session_id)
        reg = get_mode_registry()
        mode = reg.get_mode(mode_id)
        details = {
            "mode": mode.model_dump() if mode else None,
            "timer_state": st.get("timer_state"),
            "mode_state": st.get("mode_state"),
        }
        ok = True
        if exp.get("expected_mode_type") and mode:
            ok = ok and mode.mode_type == exp["expected_mode_type"]
        evs = list((st.get("mode_state") or {}).get("constraint_events") or [])
        types = [e.get("type") for e in evs]
        req = exp.get("required_constraint_event_types") or []
        for t in req:
            ok = ok and t in types
        if exp.get("min_constraint_events") is not None:
            ok = ok and len(evs) >= int(exp["min_constraint_events"])
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=ok,
            score=1.0 if ok else 0.0,
            details=details,
            metadata={"session_id": ctx.session_id},
        )
