"""Attach sessions to a learner and update profile + timeline."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.audio.analysis.pipeline.report_store import SpeechReportStore
from app.learner.aggregation.skill_aggregator import compute_session_skill_scores
from app.learner.aggregation.trend_analyzer import build_skill_scores_from_timeline, rank_weak_strong
from app.learner.config import LearnerConfig, get_learner_config
from app.learner.schemas.learner import LearnerProfile
from app.learner.schemas.progress import ProgressPoint
from app.learner.store.file_store import LearnerFileStore
from app.runtime.session.manager import SessionManager


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_speech_report(speech_report_dir: Path, session_id: str) -> dict[str, Any] | None:
    store = SpeechReportStore(speech_report_dir)
    rep = store.load_session_report(session_id)
    if rep is None:
        return None
    return rep.model_dump()


def _refresh_profile(
    profile: LearnerProfile,
    timeline: list[dict[str, Any]],
    cfg: LearnerConfig,
) -> LearnerProfile:
    skills = build_skill_scores_from_timeline(
        timeline,
        recent_window=cfg.recent_window,
        baseline_window=cfg.baseline_window,
    )
    weak, strong, focus = rank_weak_strong(skills)
    agg = {
        "skill_snapshot": [s.model_dump() for s in skills[:16]],
        "weak_skills": weak,
        "strong_skills": strong,
    }
    trend = {
        "weak_skills": weak,
        "strong_skills": strong,
        "focus_skills": focus,
    }
    profile.total_sessions = len(profile.session_ids)
    profile.weak_skills = weak
    profile.strong_skills = strong
    profile.current_focus_skills = focus
    profile.aggregate_metrics = agg
    profile.trend_summary = trend
    profile.metadata = {
        **(profile.metadata or {}),
        "profile_rebuilt_at": _utc_now(),
    }
    return profile


class SessionIngestor:
    def __init__(
        self,
        learner_store: LearnerFileStore,
        session_manager: SessionManager,
        *,
        speech_report_dir: Path,
        cfg: LearnerConfig | None = None,
    ) -> None:
        self._store = learner_store
        self._sessions = session_manager
        self._speech_dir = speech_report_dir
        self._cfg = cfg or get_learner_config()

    def ingest(
        self,
        learner_id: str,
        session_id: str,
        *,
        skip_if_duplicate: bool = True,
    ) -> ProgressPoint:
        prof = self._store.load_learner_profile(learner_id)
        if prof is None:
            raise ValueError(f"learner not found: {learner_id}")
        timeline_pre = self._store.load_timeline(learner_id)
        if skip_if_duplicate:
            for p in timeline_pre:
                if p.get("session_id") == session_id:
                    return ProgressPoint.model_validate(p)

        ctx = self._sessions.load(session_id)
        if ctx is None:
            raise ValueError(f"session not found: {session_id}")

        speech = _load_speech_report(self._speech_dir, session_id)
        scores, metrics_bundle = compute_session_skill_scores(ctx, speech_report=speech)

        created = str(ctx.metadata.get("created_at") or _utc_now())
        point = ProgressPoint(
            point_id=str(uuid.uuid4()),
            learner_id=learner_id,
            session_id=session_id,
            created_at=created,
            metrics=metrics_bundle,
            skill_scores=scores,
            metadata={"ingested_at": _utc_now()},
        )

        timeline = self._store.load_timeline(learner_id)
        timeline.append(point.model_dump())
        prof.session_ids = list(dict.fromkeys([*prof.session_ids, session_id]))
        prof = _refresh_profile(prof, timeline, self._cfg)
        self._store.save_timeline(learner_id, timeline)
        self._store.save_learner_profile(prof)
        return point


def ingest_session_for_learner(
    learner_id: str,
    session_id: str,
    *,
    learner_store: LearnerFileStore,
    session_manager: SessionManager,
    speech_report_dir: Path,
    cfg: LearnerConfig | None = None,
) -> ProgressPoint:
    return SessionIngestor(learner_store, session_manager, speech_report_dir=speech_report_dir, cfg=cfg).ingest(
        learner_id, session_id
    )
