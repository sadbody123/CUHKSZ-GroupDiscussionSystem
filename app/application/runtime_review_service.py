"""Application service for runtime V2 review workflow."""

from __future__ import annotations

from app.agent_runtime_v2.facade.runtime_factory import create_runtime_facade
from app.application.config import AppConfig
from app.application.session_service import SessionService


class RuntimeReviewService:
    def __init__(self, config: AppConfig, sessions: SessionService) -> None:
        self._config = config
        self._sessions = sessions
        self._runtime = create_runtime_facade(config, sessions)
        if self._runtime is None:
            raise ValueError("Runtime review service requires AGENT_RUNTIME_BACKEND=v2")

    def list_pending_reviews(self) -> list[dict]:
        return self._runtime.list_pending_reviews()

    def list_reviews(
        self,
        *,
        status: str | None = None,
        session_id: str | None = None,
        topic_id: str | None = None,
    ) -> list[dict]:
        return self._runtime.list_reviews(status=status, session_id=session_id, topic_id=topic_id)

    def get_review(self, review_id: str) -> dict | None:
        return self._runtime.get_review(review_id)

    def approve_review(
        self,
        review_id: str,
        *,
        action: str = "approve",
        expected_version: int | None = None,
        updated_by: str | None = None,
        payload: dict | None = None,
    ) -> dict:
        _payload = payload or {}
        if action == "reject":
            return self._runtime.reject_review(
                review_id,
                reason=str(_payload.get("reason") or ""),
                expected_version=expected_version,
                updated_by=updated_by,
            )
        return self._runtime.approve_review(
            review_id,
            action="approve",
            expected_version=expected_version,
            updated_by=updated_by,
            payload=_payload,
        )

    def reject_review(
        self,
        review_id: str,
        *,
        reason: str | None = None,
        expected_version: int | None = None,
        updated_by: str | None = None,
    ) -> dict:
        return self._runtime.reject_review(
            review_id,
            reason=reason,
            expected_version=expected_version,
            updated_by=updated_by,
        )

    def apply_edited_draft(
        self,
        review_id: str,
        *,
        edited_text: str,
        expected_version: int | None = None,
        updated_by: str | None = None,
        note: str | None = None,
        resume_after_apply: bool = False,
        additional_steps: int = 1,
    ) -> dict:
        return self._runtime.apply_edited_draft(
            review_id,
            edited_text=edited_text,
            expected_version=expected_version,
            updated_by=updated_by,
            note=note,
            resume_after_apply=resume_after_apply,
            additional_steps=additional_steps,
        )

    def resume_from_review(self, review_id: str, *, additional_steps: int = 1) -> dict:
        return self._runtime.resume_from_review(review_id, additional_steps=additional_steps)

    def get_metrics(self) -> dict:
        return self._runtime.get_review_metrics()
