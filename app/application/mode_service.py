"""Practice modes, drills, and assessment simulation orchestration."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.session_service import SessionService
from app.integration_logging import warn_optional_hook_failed
from app.modes.constants import SIMULATION_NOTE
from app.modes.engines.constraint_engine import evaluate_user_turn_constraints, merge_constraint_events
from app.modes.engines.drill_generator import generate_drills_for_profile
from app.modes.engines.progress_tracker import update_progress_after_turn
from app.modes.engines.timer_policy import compute_timer_state
from app.modes.loaders.yaml_loader import get_mode_registry
from app.modes.planning.learner_plan_bridge import step_to_launch_spec
from app.modes.planning.session_launch_spec import SessionLaunchSpec
from app.modes.schemas.report import ModeSessionReport
from app.modes.store.mode_report_store import ModeReportStore
from app.runtime.schemas.session import SessionContext


class ModeService:
    def __init__(self, config: AppConfig | None = None, session_service: SessionService | None = None) -> None:
        self._config = config or get_app_config()
        self._sessions = session_service or SessionService(self._config)
        self._reports = ModeReportStore(self._config.mode_reports_dir)

    def list_modes(self) -> list[dict[str, Any]]:
        return [m.model_dump() for m in get_mode_registry().modes.values()]

    def get_mode(self, mode_id: str) -> dict[str, Any] | None:
        m = get_mode_registry().get_mode(mode_id)
        return m.model_dump() if m else None

    def list_presets(self) -> list[dict[str, Any]]:
        return [p.model_dump() for p in get_mode_registry().presets.values()]

    def get_preset(self, preset_id: str) -> dict[str, Any] | None:
        p = get_mode_registry().get_preset(preset_id)
        return p.model_dump() if p else None

    def list_assessment_templates(self) -> list[dict[str, Any]]:
        return [t.model_dump() for t in get_mode_registry().assessment_templates.values()]

    def get_assessment_template(self, template_id: str) -> dict[str, Any] | None:
        t = get_mode_registry().get_template(template_id)
        return t.model_dump() if t else None

    def generate_drills_for_learner(self, learner_id: str) -> list[dict[str, Any]]:
        from app.application.learner_service import LearnerService

        lsvc = LearnerService(self._config, self._sessions)
        prof = lsvc.get_learner_profile(learner_id)
        if not prof:
            raise ValueError(f"learner not found: {learner_id}")
        return generate_drills_for_profile(prof, max_drills=12)

    def resolve_session_launch_spec(
        self,
        *,
        snapshot_id: str,
        learner_id: str | None,
        plan_step: dict[str, Any],
    ) -> SessionLaunchSpec:
        return step_to_launch_spec(plan_step, snapshot_id=snapshot_id, learner_id=learner_id)

    def get_mode_status(self, session_id: str) -> dict[str, Any]:
        ctx = self._sessions.get_session(session_id)
        reg = get_mode_registry()
        mid = ctx.mode_id or self._config.default_mode_id
        mode = reg.get_mode(mid)
        tpl = reg.get_template(ctx.assessment_template_id) if ctx.assessment_template_id else None
        timer_state = compute_timer_state(ctx, mode=mode, template=tpl)
        return {
            "session_id": session_id,
            "mode_id": ctx.mode_id,
            "preset_id": ctx.preset_id,
            "drill_id": ctx.drill_id,
            "assessment_template_id": ctx.assessment_template_id,
            "mode_state": ctx.mode_state,
            "timer_state": timer_state,
            "simulation_note": SIMULATION_NOTE if ctx.assessment_template_id else None,
        }

    def on_user_turn_committed(self, session_id: str, text: str) -> None:
        if not self._config.enable_practice_modes:
            return
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            return
        reg = get_mode_registry()
        mid = ctx.mode_id or self._config.default_mode_id
        mode = reg.get_mode(mid)
        drill = reg.get_drill(ctx.drill_id) if ctx.drill_id else None
        ev = evaluate_user_turn_constraints(ctx, text, mode=mode, drill=drill)
        merge_constraint_events(ctx, ev)
        update_progress_after_turn(ctx)
        tpl = reg.get_template(ctx.assessment_template_id) if ctx.assessment_template_id else None
        ctx.timer_state = compute_timer_state(ctx, mode=mode, template=tpl)
        self._sessions.manager.save(ctx)

    def on_turn_saved(self, session_id: str) -> None:
        if not self._config.enable_practice_modes:
            return
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            return
        reg = get_mode_registry()
        mid = ctx.mode_id or self._config.default_mode_id
        mode = reg.get_mode(mid)
        tpl = reg.get_template(ctx.assessment_template_id) if ctx.assessment_template_id else None
        update_progress_after_turn(ctx)
        ctx.timer_state = compute_timer_state(ctx, mode=mode, template=tpl)
        self._sessions.manager.save(ctx)

    def build_mode_report(self, session_id: str, *, persist: bool = True) -> ModeSessionReport:
        ctx = self._sessions.get_session(session_id)
        reg = get_mode_registry()
        rid = str(uuid.uuid4())
        rep = ModeSessionReport(
            report_id=rid,
            session_id=session_id,
            mode_id=ctx.mode_id,
            preset_id=ctx.preset_id,
            drill_id=ctx.drill_id,
            assessment_template_id=ctx.assessment_template_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            phase_progress=dict(ctx.mode_state or {}),
            timer_events=[dict(ctx.timer_state or {})],
            constraint_events=list((ctx.mode_state or {}).get("constraint_events") or []),
            success_checks=list((ctx.mode_state or {}).get("success_checks") or []),
            strengths=[],
            risks=[],
            recommended_next_actions=[],
            proxy_notes=[SIMULATION_NOTE] if ctx.assessment_template_id else [],
            metadata={"practice_report": True, "not_an_exam_score": True},
        )
        if ctx.coach_report and isinstance(ctx.coach_report, dict):
            rep.strengths = list(ctx.coach_report.get("strengths") or [])[:8]
            rep.risks = list(ctx.coach_report.get("risks") or [])[:8]
        if persist:
            self._reports.save(rep)
            ctx.mode_report_id = rid
            self._sessions.manager.save(ctx)
            try:
                from app.ops.artifacts.registry import ArtifactRegistry

                ArtifactRegistry().register_artifact(
                    self._config.mode_reports_dir / f"{session_id}_{rid}.json",
                    "mode_report",
                    metadata={"session_id": session_id},
                )
            except Exception as exc:
                warn_optional_hook_failed("artifacts.register_mode_report", exc, session_id=session_id)
        return rep

    def maybe_auto_mode_report(self, session_id: str) -> None:
        if not self._config.auto_generate_mode_report or not self._config.enable_practice_modes:
            return
        try:
            self.build_mode_report(session_id, persist=True)
        except Exception as exc:
            warn_optional_hook_failed("mode.maybe_auto_mode_report", exc, session_id=session_id)

    def load_or_build_mode_report(self, session_id: str, *, persist_if_built: bool = False) -> ModeSessionReport:
        ex = self._reports.load_by_session(session_id)
        if ex:
            return ex
        return self.build_mode_report(session_id, persist=persist_if_built)
