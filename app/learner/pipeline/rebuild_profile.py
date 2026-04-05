"""Rebuild learner timeline + profile from associated session ids."""

from __future__ import annotations

from pathlib import Path

from app.learner.aggregation.session_ingest import SessionIngestor
from app.learner.config import LearnerConfig, get_learner_config
from app.learner.store.file_store import LearnerFileStore
from app.runtime.session.manager import SessionManager


def rebuild_learner_from_sessions(
    learner_id: str,
    *,
    learner_store: LearnerFileStore,
    session_manager: SessionManager,
    speech_report_dir: Path,
    cfg: LearnerConfig | None = None,
) -> None:
    prof = learner_store.load_learner_profile(learner_id)
    if prof is None:
        raise ValueError(f"learner not found: {learner_id}")
    cfg = cfg or get_learner_config()
    ids = list(prof.session_ids)
    learner_store.save_timeline(learner_id, [])
    prof.session_ids = []
    prof.total_sessions = 0
    learner_store.save_learner_profile(prof)

    ingestor = SessionIngestor(
        learner_store,
        session_manager,
        speech_report_dir=speech_report_dir,
        cfg=cfg,
    )
    for sid in ids:
        ingestor.ingest(learner_id, sid, skip_if_duplicate=False)
