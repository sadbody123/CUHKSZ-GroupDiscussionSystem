"""seat_allocation_case — roster present yields a next speaker plan."""

from __future__ import annotations

import tempfile
from dataclasses import asdict
from pathlib import Path

from app.application.config import get_app_config
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.group_sim.engines.turn_allocator import allocate_next_speaker


def run_seat_allocation_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    snapshot_id = str(inp.get("snapshot_id") or snapshot_dir.name)
    topic_id = str(inp.get("topic_id") or "tc-campus-ai")

    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        cfg = get_app_config().model_copy(
            update={
                "session_storage_dir": (tmp / "sessions").resolve(),
                "learner_storage_dir": (tmp / "learners").resolve(),
                "speech_report_dir": (tmp / "speech").resolve(),
                "mode_reports_dir": (tmp / "mode_reports").resolve(),
                "group_reports_dir": (tmp / "group_reports").resolve(),
                "snapshot_root": snapshot_dir.parent.resolve(),
                "enable_group_sim": True,
            }
        )
        for d in (tmp / "sessions", tmp / "learners", tmp / "speech", tmp / "mode_reports", tmp / "group_reports"):
            d.mkdir(parents=True, exist_ok=True)

        svc = SessionService(cfg)
        ctx = svc.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance="for",
            provider_name="mock",
            roster_template_id=str(inp.get("roster_template_id") or "gd_4p_balanced"),
            user_participant_id=str(inp.get("user_participant_id") or "for_a"),
            source="eval",
        )
        plan = allocate_next_speaker(ctx, None)
        ok = plan is not None and bool(plan.participant_id)
        if exp.get("min_participants"):
            ok = ok and len(ctx.participants or []) >= int(exp["min_participants"])
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=ok,
            score=1.0 if ok else 0.0,
            details={"plan": asdict(plan) if plan else None, "participant_count": len(ctx.participants or [])},
            metadata={"session_id": ctx.session_id},
        )
