"""Review workspace application service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.integration_logging import warn_optional_hook_failed
from app.application.session_service import SessionService
from app.review.config import ReviewConfig, review_paths_from_app_config
from app.review.engines.calibration_engine import build_calibration_report
from app.review.pipeline.create_review_pack import run_create_review_pack
from app.review.pipeline.export_review_report import export_calibration_json, export_calibration_markdown
from app.review.pipeline.rebuild_calibration import run_rebuild_calibration
from app.review.pipeline.submit_review import run_submit_review
from app.review.schemas.calibration import CalibrationReport
from app.review.schemas.report import HumanReview
from app.review.schemas.reviewer import ReviewerProfile
from app.review.store.queue_index import QueueIndex
from app.review.store.review_store import ReviewStore
from app.review.store.reviewer_store import ReviewerStore


class ReviewService:
    def __init__(
        self,
        config: AppConfig | None = None,
        session_service: SessionService | None = None,
    ) -> None:
        self._config = config or get_app_config()
        self._sessions = session_service or SessionService(self._config)
        paths = review_paths_from_app_config(self._config)
        self._reviewers = ReviewerStore(paths.reviewer_root)
        self._store = ReviewStore(
            paths.review_packs_dir,
            paths.submissions_dir,
            paths.calibration_dir,
            paths.reviewed_outputs_dir,
        )
        self._rcfg = ReviewConfig.from_app_config(self._config)
        self._queue = QueueIndex(paths.queue_index_path, max_items=self._config.review_queue_max_items)

    def _ensure_enabled(self) -> None:
        if not self._config.enable_review_workspace:
            raise ValueError("review workspace disabled")

    def create_reviewer(
        self,
        *,
        reviewer_id: str,
        display_name: str,
        role_title: str | None = None,
        notes: list[str] | None = None,
    ) -> ReviewerProfile:
        self._ensure_enabled()
        now = datetime.now(timezone.utc).isoformat()
        p = ReviewerProfile(
            reviewer_id=reviewer_id,
            display_name=display_name,
            role_title=role_title,
            created_at=now,
            preferred_rubric_id=self._config.default_review_rubric_id,
            notes=list(notes or []),
            metadata={},
        )
        return self._reviewers.create_reviewer(p)

    def list_reviewers(self) -> list[ReviewerProfile]:
        self._ensure_enabled()
        return self._reviewers.list_reviewers()

    def get_reviewer(self, reviewer_id: str) -> ReviewerProfile | None:
        self._ensure_enabled()
        return self._reviewers.load_reviewer(reviewer_id)

    def create_review_pack(self, session_id: str) -> object:
        self._ensure_enabled()
        return run_create_review_pack(
            session_id,
            config=self._config,
            sessions=self._sessions,
            store=self._store,
            queue=self._queue,
        )

    def list_review_packs(self) -> list:
        self._ensure_enabled()
        return self._store.list_review_packs()

    def get_review_pack(self, review_pack_id: str):
        self._ensure_enabled()
        p = self._store.load_review_pack(review_pack_id)
        if not p:
            raise ValueError("review pack not found")
        return p

    def submit_human_review(
        self,
        *,
        review_pack_id: str,
        reviewer_id: str,
        payload: dict[str, Any],
    ) -> HumanReview:
        self._ensure_enabled()
        pack = self._store.load_review_pack(review_pack_id)
        if not pack:
            raise ValueError("review pack not found")
        ctx = self._sessions.manager.load(pack.session_id)
        coach = ctx.coach_report if ctx else None
        hr = run_submit_review(
            review_pack_id=review_pack_id,
            reviewer_id=reviewer_id,
            payload=payload,
            review_store=self._store,
            reviewer_store=self._reviewers,
            queue=self._queue,
            cfg=self._rcfg,
            coach_report=coach,
        )
        try:
            run_rebuild_calibration(
                review_pack_id=review_pack_id,
                review_id=hr.review_id,
                coach_report=coach,
                store=self._store,
            )
        except Exception as exc:
            warn_optional_hook_failed(
                "review.rebuild_calibration_after_submit",
                exc,
                review_pack_id=review_pack_id,
                review_id=hr.review_id,
            )
        return hr

    def get_session_reviews(self, session_id: str) -> list[HumanReview]:
        self._ensure_enabled()
        return self._store.list_reviews_for_session(session_id)

    def generate_calibration_report(self, review_pack_id: str, review_id: str) -> CalibrationReport:
        self._ensure_enabled()
        ctx = self._sessions.manager.load(self._store.load_review_pack(review_pack_id).session_id)  # type: ignore[union-attr]
        coach = ctx.coach_report if ctx else None
        return run_rebuild_calibration(  # type: ignore[return-value]
            review_pack_id=review_pack_id,
            review_id=review_id,
            coach_report=coach,
            store=self._store,
        )

    def get_review_summary(self, session_id: str) -> dict[str, Any]:
        self._ensure_enabled()
        reviews = self._store.list_reviews_for_session(session_id)
        packs = [p for p in self._store.list_review_packs() if p.session_id == session_id]
        latest_cal = None
        if packs:
            pid = packs[-1].review_pack_id
            for r in reviews:
                c = self._store.load_calibration_report(pid, r.review_id)
                if c:
                    latest_cal = c.model_dump()
                    break
        return {
            "session_id": session_id,
            "review_count": len(reviews),
            "pack_count": len(packs),
            "latest_calibration": latest_cal,
        }

    def export_review_report(
        self,
        review_pack_id: str,
        *,
        review_id: str | None = None,
        output_file: Path | None = None,
        as_markdown: bool = False,
    ) -> dict[str, Any] | str:
        self._ensure_enabled()
        pack = self._store.load_review_pack(review_pack_id)
        if not pack:
            raise ValueError("review pack not found")
        reviews = self._store.list_human_reviews_for_pack(review_pack_id)
        rid = review_id or (reviews[-1].review_id if reviews else None)
        if not rid:
            raise ValueError("no human review for pack")
        cal = self._store.load_calibration_report(review_pack_id, rid)
        if not cal:
            ctx = self._sessions.manager.load(pack.session_id)
            coach = ctx.coach_report if ctx else None
            hr = self._store.load_human_review(rid)
            if not hr:
                raise ValueError("human review not found")
            cal = build_calibration_report(
                review_pack_id=review_pack_id,
                session_id=pack.session_id,
                review_id=rid,
                coach_report=coach,
                human=hr,
            )
            self._store.save_calibration_report(cal)
        data = cal.model_dump()
        if output_file:
            if as_markdown:
                export_calibration_markdown(data, output_file)
            else:
                export_calibration_json(data, output_file)
            return {"written": str(output_file)}
        return data

    def compare_ai_vs_human(self, review_pack_id: str) -> dict[str, Any]:
        self._ensure_enabled()
        pack = self._store.load_review_pack(review_pack_id)
        if not pack:
            raise ValueError("review pack not found")
        reviews = self._store.list_human_reviews_for_pack(review_pack_id)
        if not reviews:
            raise ValueError("no human review submitted")
        rid = reviews[-1].review_id
        ctx = self._sessions.manager.load(pack.session_id)
        coach = ctx.coach_report if ctx else None
        hr = reviews[-1]
        rep = build_calibration_report(
            review_pack_id=review_pack_id,
            session_id=pack.session_id,
            review_id=rid,
            coach_report=coach,
            human=hr,
        )
        return rep.model_dump()

    def list_queue_items(self, **kwargs: Any) -> list:
        self._ensure_enabled()
        return self._queue.list_queue_items(**kwargs)

    def export_reviewed_feedback(self, review_pack_id: str) -> dict[str, Any]:
        self._ensure_enabled()
        raw = self._store.load_reviewed_output(review_pack_id)
        if not raw:
            raise ValueError("reviewed output not found; submit review with approved overrides first")
        return raw
