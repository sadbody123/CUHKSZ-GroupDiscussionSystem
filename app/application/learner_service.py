"""Application orchestration for learner analytics (phase 11)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.integration_logging import warn_optional_hook_failed
from app.application.session_service import SessionService
from app.learner.aggregation.session_ingest import SessionIngestor
from app.learner.config import LearnerConfig, get_learner_config
from app.learner.pipeline.export_report import build_learner_report_dict
from app.learner.pipeline.rebuild_profile import rebuild_learner_from_sessions
from app.learner.planning.plan_generator import generate_learning_plan
from app.learner.recommendation.engine import build_recommendations
from app.learner.schemas.learner import LearnerProfile
from app.learner.schemas.plan import LearningPlan
from app.learner.schemas.recommendation import RecommendationItem
from app.learner.store.file_store import LearnerFileStore
from app.ops.artifacts.registry import ArtifactRegistry


class LearnerService:
    def __init__(self, config: AppConfig | None = None, session_service: SessionService | None = None) -> None:
        self._config = config or get_app_config()
        self._sessions = session_service or SessionService(self._config)
        self._store = LearnerFileStore(self._config.learner_storage_dir)
        self._lcfg = get_learner_config()

    def _ingestor(self) -> SessionIngestor:
        return SessionIngestor(
            self._store,
            self._sessions.manager,
            speech_report_dir=self._config.speech_report_dir,
            cfg=self._lcfg,
        )

    def create_learner(self, learner_id: str, display_name: str | None = None) -> LearnerProfile:
        if not self._config.enable_learner_analytics:
            raise ValueError("learner analytics disabled")
        return self._store.create_learner(learner_id, display_name=display_name)

    def list_learners(self) -> list[dict[str, Any]]:
        from app.learner.store.index import LearnerIndex

        return LearnerIndex(self._store.root).summaries()

    def get_learner_profile(self, learner_id: str) -> LearnerProfile | None:
        return self._store.load_learner_profile(learner_id)

    def get_timeline(self, learner_id: str) -> list[dict[str, Any]]:
        return self._store.load_timeline(learner_id)

    def attach_session_to_learner(self, learner_id: str, session_id: str, *, ingest: bool = True) -> dict[str, Any]:
        prof = self._store.load_learner_profile(learner_id)
        if prof is None:
            raise ValueError(f"learner not found: {learner_id}")
        ctx = self._sessions.manager.load(session_id)
        if ctx is None:
            raise ValueError(f"session not found: {session_id}")
        ctx.learner_id = learner_id
        self._sessions.manager.save(ctx)
        if session_id not in prof.session_ids:
            prof.session_ids.append(session_id)
        prof.total_sessions = len(prof.session_ids)
        self._store.save_learner_profile(prof)
        if ingest and self._config.enable_learner_analytics:
            try:
                self._ingestor().ingest(learner_id, session_id, skip_if_duplicate=True)
            except Exception as exc:
                warn_optional_hook_failed("learner.ingest_on_attach", exc, learner_id=learner_id, session_id=session_id)
        return {"learner_id": learner_id, "session_id": session_id, "ingested": bool(ingest)}

    def rebuild_learner_profile(self, learner_id: str) -> None:
        rebuild_learner_from_sessions(
            learner_id,
            learner_store=self._store,
            session_manager=self._sessions.manager,
            speech_report_dir=self._config.speech_report_dir,
            cfg=self._lcfg,
        )

    def _snapshot_dir_for_learner(self, profile: LearnerProfile) -> Path | None:
        """Use last associated session's snapshot_dir, else None."""
        for sid in reversed(profile.session_ids):
            ctx = self._sessions.manager.load(sid)
            if ctx and ctx.snapshot_dir:
                return Path(ctx.snapshot_dir)
        return None

    def _practiced_topics(self, learner_id: str) -> set[str]:
        out: set[str] = set()
        for pt in self._store.load_timeline(learner_id):
            tid = (pt.get("metrics") or {}).get("topic_id")
            if tid:
                out.add(str(tid))
        return out

    def _has_audio_history(self, profile: LearnerProfile) -> bool:
        for sid in profile.session_ids:
            ctx = self._sessions.manager.load(sid)
            if ctx and (ctx.audio_asset_ids or []):
                return True
        return False

    def _max_turn_words_hint(self, profile: LearnerProfile) -> int:
        m = 0
        for sid in profile.session_ids[-3:]:
            ctx = self._sessions.manager.load(sid)
            if not ctx or not ctx.turns:
                continue
            for t in ctx.turns:
                m = max(m, len((t.text or "").split()))
        return m

    def get_recommendations(self, learner_id: str) -> list[RecommendationItem]:
        prof = self._store.load_learner_profile(learner_id)
        if prof is None:
            raise ValueError(f"learner not found: {learner_id}")
        snap = self._snapshot_dir_for_learner(prof)
        if snap is None:
            raise ValueError("no snapshot context for learner — attach at least one session with a snapshot")
        cfg = get_learner_config()
        return build_recommendations(
            prof,
            snap,
            cfg=cfg,
            practiced_topic_ids=self._practiced_topics(learner_id),
            max_turn_words_hint=self._max_turn_words_hint(prof),
            has_audio_history=self._has_audio_history(prof),
        )

    def generate_learning_plan(self, learner_id: str, horizon: int | None = None, *, persist: bool = True) -> LearningPlan:
        prof = self._store.load_learner_profile(learner_id)
        if prof is None:
            raise ValueError(f"learner not found: {learner_id}")
        hz = horizon if horizon is not None else self._config.default_learning_plan_horizon
        recs = self.get_recommendations(learner_id)
        plan = generate_learning_plan(prof.learner_id, prof.weak_skills or [], recs, horizon=hz)
        if persist:
            self._store.save_plan(learner_id, plan)
            ArtifactRegistry().register_artifact(
                self._store.learner_dir(learner_id) / "plans" / f"{plan.plan_id}.json",
                "learning_plan",
                metadata={"learner_id": learner_id},
            )
        return plan

    def build_learner_report(self, learner_id: str, *, persist_report: bool = False) -> dict[str, Any]:
        prof = self._store.load_learner_profile(learner_id)
        if prof is None:
            raise ValueError(f"learner not found: {learner_id}")
        timeline = self._store.load_timeline(learner_id)
        recs = self.get_recommendations(learner_id)
        plan = self.generate_learning_plan(learner_id, horizon=self._config.default_learning_plan_horizon, persist=False)
        rep = build_learner_report_dict(
            prof.model_dump(),
            timeline,
            [r.model_dump() for r in recs],
            plan.model_dump(),
        )
        if persist_report:
            self._store.save_report(learner_id, rep)
            ArtifactRegistry().register_artifact(
                self._store.learner_dir(learner_id) / "reports" / f"{rep['report_id']}.json",
                "learner_report",
                metadata={"learner_id": learner_id},
            )
        return rep

    def export_learner_report(self, learner_id: str, output_file: Path | None = None) -> dict[str, Any]:
        rep = self.build_learner_report(learner_id, persist_report=True)
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return rep

    def maybe_auto_ingest_after_feedback(self, session_id: str) -> None:
        if not self._config.auto_ingest_session_to_learner or not self._config.enable_learner_analytics:
            return
        ctx = self._sessions.manager.load(session_id)
        if not ctx or not ctx.learner_id:
            return
        try:
            self._ingestor().ingest(ctx.learner_id, session_id, skip_if_duplicate=True)
        except Exception as exc:
            warn_optional_hook_failed(
                "learner.maybe_auto_ingest_after_feedback",
                exc,
                learner_id=ctx.learner_id,
                session_id=session_id,
            )
