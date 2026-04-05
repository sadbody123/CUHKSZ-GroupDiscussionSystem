"""assessment_simulation_case — template applies timer + simulation disclaimer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.application.config import get_app_config
from app.application.mode_service import ModeService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_assessment_simulation_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    snapshot_id = str(inp.get("snapshot_id") or snapshot_dir.name)
    topic_id = str(inp.get("topic_id") or "tc-campus-ai")
    template_id = str(inp.get("assessment_template_id") or "gd_assessment_4p_v1")
    mode_id = str(inp.get("mode_id") or "assessment_simulation")
    preset_id = inp.get("preset_id")

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
        msvc = ModeService(cfg, svc)
        ctx = svc.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance="neutral",
            provider_name="mock",
            runtime_profile_id=profile_id or inp.get("runtime_profile_id") or "default",
            mode_id=mode_id,
            preset_id=preset_id,
            assessment_template_id=template_id,
            source="eval",
        )
        st = msvc.get_mode_status(ctx.session_id)
        timer = st.get("timer_state") or {}
        ok = True
        if exp.get("simulation_note_non_empty"):
            ok = ok and bool(st.get("simulation_note"))
        for field in exp.get("required_timer_fields") or ["discussion_seconds", "prep_seconds"]:
            ok = ok and field in timer
        if exp.get("expected_assessment_phase_estimate"):
            ok = ok and timer.get("assessment_phase_estimate") == exp["expected_assessment_phase_estimate"]
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=ok,
            score=1.0 if ok else 0.0,
            details={"timer_state": timer, "simulation_note": st.get("simulation_note")},
            metadata={"session_id": ctx.session_id},
        )
