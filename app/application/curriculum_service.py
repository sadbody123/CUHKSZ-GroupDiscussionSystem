"""Curriculum packs, assignments, delivery orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.session_service import SessionService
from app.curriculum.constants import STEP_COMPLETED, STEP_LAUNCHED, TRAINING_DELIVERY_NOTE
from app.curriculum.engines.completion_engine import evaluate_step_completion
from app.curriculum.engines.delivery_analytics import (
    build_assignment_report,
    build_delivery_summary,
    recompute_assignment_status,
)
from app.curriculum.engines.launch_bridge import build_session_launch_kwargs, find_step
from app.curriculum.engines.planning_bridge import pack_from_learning_plan
from app.curriculum.engines.attempt_tracker import build_attempt
from app.curriculum.pipeline.export_assignment_report import export_report_json
from app.curriculum.schemas.assignment import AssignmentSpec
from app.curriculum.schemas.pack import CurriculumPack
from app.curriculum.store.assignment_store import AssignmentStore
from app.curriculum.store.index import learner_assignment_ids
from app.curriculum.store.pack_store import PackStore


class CurriculumService:
    def __init__(
        self,
        config: AppConfig | None = None,
        session_service: SessionService | None = None,
    ) -> None:
        self._config = config or get_app_config()
        self._sessions = session_service or SessionService(self._config)
        self._packs = PackStore(self._config.curriculum_pack_builtin_dir, self._config.curriculum_custom_pack_dir)
        self._assignments = AssignmentStore(self._config.assignment_storage_dir)

    def _ensure(self) -> None:
        if not self._config.enable_curriculum_delivery:
            raise ValueError("curriculum delivery disabled")

    def list_curriculum_packs(self) -> list[CurriculumPack]:
        self._ensure()
        return self._packs.list_packs()

    def get_curriculum_pack(self, pack_id: str) -> CurriculumPack:
        self._ensure()
        p = self._packs.load_pack(pack_id)
        if not p:
            raise ValueError(f"pack not found: {pack_id}")
        return p

    def create_curriculum_pack_from_learning_plan(
        self,
        *,
        learner_id: str,
        horizon: int,
        output_pack_id: str,
        display_name: str | None = None,
    ) -> CurriculumPack:
        self._ensure()
        if not self._config.enable_plan_to_pack_bridge:
            raise ValueError("plan to pack bridge disabled")
        from app.application.learner_service import LearnerService

        lsvc = LearnerService(self._config, self._sessions)
        plan = lsvc.generate_learning_plan(learner_id, horizon=horizon, persist=False)
        pack = pack_from_learning_plan(
            plan,
            pack_id=output_pack_id,
            display_name=display_name or f"Plan pack for {learner_id}",
        )
        self._packs.save_custom_pack(pack)
        return pack

    def create_assignment(
        self,
        *,
        pack_id: str,
        learner_ids: list[str],
        created_by: str | None,
        title: str,
        description: str | None = None,
        due_at: str | None = None,
    ) -> AssignmentSpec:
        self._ensure()
        from app.curriculum.pipeline.create_assignment import run_create_assignment

        pack = self.get_curriculum_pack(pack_id)
        spec = run_create_assignment(
            pack,
            self._assignments,
            learner_ids=learner_ids,
            title=title,
            created_by=created_by,
            description=description,
            due_at=due_at,
        )
        return spec  # type: ignore[no-any-return]

    def list_assignments(self, *, learner_id: str | None = None) -> list[AssignmentSpec]:
        self._ensure()
        rows = self._assignments.list_assignments()
        if learner_id:
            allowed = set(learner_assignment_ids(self._config.assignment_storage_dir, learner_id))
            rows = [a for a in rows if a.assignment_id in allowed or learner_id in a.learner_ids]
        return rows

    def get_assignment(self, assignment_id: str) -> AssignmentSpec:
        self._ensure()
        a = self._assignments.load_assignment(assignment_id)
        if not a:
            raise ValueError("assignment not found")
        return a

    def get_assignment_progress(self, assignment_id: str) -> dict[str, Any]:
        self._ensure()
        spec = self.get_assignment(assignment_id)
        d = self._assignments.load_delivery_summary(assignment_id)
        if not d:
            d = build_delivery_summary(spec)
            self._assignments.save_delivery_summary(assignment_id, d)
        return {"assignment": spec.model_dump(), "delivery": d.model_dump()}

    def launch_assignment_step_session(
        self,
        *,
        assignment_id: str,
        pack_step_id: str,
        snapshot_id: str,
        provider_name: str = "mock",
        learner_id: str | None = None,
    ) -> dict[str, Any]:
        self._ensure()
        spec = self.get_assignment(assignment_id)
        pack = self.get_curriculum_pack(spec.pack_id)
        kwargs = build_session_launch_kwargs(
            pack,
            pack_step_id,
            learner_id=learner_id or (spec.learner_ids[0] if spec.learner_ids else None),
            snapshot_id=snapshot_id,
            provider_name=provider_name,
        )
        ac = kwargs.pop("assignment_context", {})
        ctx = self._sessions.create_session(
            snapshot_id=kwargs["snapshot_id"],
            topic_id=kwargs["topic_id"],
            user_stance=kwargs.get("user_stance"),
            provider_name=kwargs.get("provider_name"),
            runtime_profile_id=kwargs.get("runtime_profile_id"),
            learner_id=kwargs.get("learner_id"),
            mode_id=kwargs.get("mode_id"),
            preset_id=kwargs.get("preset_id"),
            drill_id=kwargs.get("drill_id"),
            assessment_template_id=kwargs.get("assessment_template_id"),
            roster_template_id=kwargs.get("roster_template_id"),
            curriculum_pack_id=kwargs.get("curriculum_pack_id"),
            assignment_id=spec.assignment_id,
            assignment_step_id=next(
                (s.assignment_step_id for s in spec.step_refs if s.pack_step_id == pack_step_id),
                None,
            ),
            audio_enabled=bool(kwargs.get("audio_enabled")),
            source="curriculum",
        )
        ctx.metadata = {
            **ctx.metadata,
            **({"assignment_context": ac} if ac else {}),
            "curriculum_pack_step_id": pack_step_id,
        }
        self._sessions.manager.save(ctx)
        for s in spec.step_refs:
            if s.pack_step_id == pack_step_id:
                s.status = STEP_LAUNCHED
                s.latest_session_id = ctx.session_id
                break
        spec.status = recompute_assignment_status(spec)
        self._assignments.save_assignment(spec)
        return {"session_id": ctx.session_id, "assignment_id": spec.assignment_id, "pack_step_id": pack_step_id}

    def attach_session_to_assignment_step(
        self,
        *,
        assignment_id: str,
        pack_step_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        self._ensure()
        spec = self.get_assignment(assignment_id)
        pack = self.get_curriculum_pack(spec.pack_id)
        st = find_step(pack, pack_step_id)
        if not st:
            raise ValueError("step not found")
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise ValueError("session not found")
        step_ref = next((s for s in spec.step_refs if s.pack_step_id == pack_step_id), None)
        if not step_ref:
            raise ValueError("assignment step ref missing")
        status, summary = evaluate_step_completion(ctx, st)
        att = build_attempt(
            assignment_id=assignment_id,
            assignment_step_id=step_ref.assignment_step_id,
            session_id=session_id,
            learner_id=ctx.learner_id,
            topic_id=ctx.topic_id,
        )
        att.outcome_summary = {**att.outcome_summary, "step_status": status, **summary}
        att.success_checks = [{"check": "completion_engine", "status": status}]
        self._assignments.append_attempt(assignment_id, att)
        step_ref.status = status
        step_ref.latest_session_id = session_id
        step_ref.completion_summary = summary
        step_ref.attempt_ids.append(att.attempt_id)
        spec.status = recompute_assignment_status(spec)
        self._assignments.save_assignment(spec)
        d = build_delivery_summary(spec)
        self._assignments.save_delivery_summary(assignment_id, d)
        rep = None
        if self._config.auto_generate_assignment_report:
            rep = self.generate_assignment_report(assignment_id)
        return {"attempt_id": att.attempt_id, "step_status": status, "report_id": rep.report_id if rep else None}

    def generate_assignment_report(self, assignment_id: str) -> Any:
        self._ensure()
        spec = self.get_assignment(assignment_id)
        pack = self.get_curriculum_pack(spec.pack_id)
        rep = build_assignment_report(spec, {"pack_id": pack.pack_id, "display_name": pack.display_name})
        self._assignments.save_report(assignment_id, rep)
        return rep

    def export_assignment_report(self, assignment_id: str, output_file: Path | None = None) -> dict[str, Any] | Any:
        self._ensure()
        rep = self._assignments.load_report(assignment_id) or self.generate_assignment_report(assignment_id)
        if output_file:
            export_report_json(rep, output_file)
            return {"written": str(output_file)}
        return rep.model_dump()

    def list_learner_assignments(self, learner_id: str) -> list[AssignmentSpec]:
        return self.list_assignments(learner_id=learner_id)

    def get_next_recommended_assignment_step(self, assignment_id: str) -> dict[str, Any] | None:
        self._ensure()
        spec = self.get_assignment(assignment_id)
        for s in sorted(spec.step_refs, key=lambda x: x.metadata.get("order", 0)):
            if s.status != STEP_COMPLETED:
                return {"pack_step_id": s.pack_step_id, "assignment_step_id": s.assignment_step_id, "status": s.status}
        return None
