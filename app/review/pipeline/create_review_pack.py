"""Pipeline: create review pack from session."""

from __future__ import annotations

from app.application.config import AppConfig
from app.review.engines.pack_builder import build_review_pack
from app.review.store.queue_index import QueueIndex
from app.review.store.review_store import ReviewStore
from app.application.session_service import SessionService


def run_create_review_pack(
    session_id: str,
    *,
    config: AppConfig,
    sessions: SessionService,
    store: ReviewStore,
    queue: QueueIndex | None = None,
):
    ctx = sessions.manager.load(session_id)
    if not ctx:
        raise ValueError("session not found")
    learner_summary = None
    if config.enable_learner_analytics and ctx.learner_id:
        try:
            from app.application.learner_service import LearnerService

            ls = LearnerService(config, sessions)
            prof = ls.get_learner_profile(ctx.learner_id)
            if prof:
                learner_summary = {"learner_id": prof.learner_id, "display_name": prof.display_name}
        except Exception:
            learner_summary = None

    pack = build_review_pack(
        ctx,
        speech_report_dir=config.speech_report_dir,
        mode_reports_dir=config.mode_reports_dir,
        group_reports_dir=config.group_reports_dir,
        learner_summary=learner_summary,
    )
    store.save_review_pack(pack)
    if queue:
        queue.enqueue_pack(review_pack_id=pack.review_pack_id, session_id=pack.session_id)
    return pack
