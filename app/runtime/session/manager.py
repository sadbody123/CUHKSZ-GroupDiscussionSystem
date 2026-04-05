"""High-level session CRUD."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.integration_logging import warn_optional_hook_failed
from app.runtime.schemas.session import SessionContext
from app.runtime.session.file_store import FileSessionStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionManager:
    def __init__(self, store: FileSessionStore | None = None) -> None:
        self.store = store or FileSessionStore()

    def create_session(
        self,
        *,
        topic_id: str,
        snapshot_dir: str,
        user_stance: str | None = None,
        provider_name: str = "mock",
        model_name: str | None = None,
        phase: str = "discussion",
        max_discussion_turns: int | None = None,
        runtime_profile_id: str | None = None,
        learner_id: str | None = None,
        mode_id: str | None = None,
        preset_id: str | None = None,
        drill_id: str | None = None,
        assessment_template_id: str | None = None,
        curriculum_pack_id: str | None = None,
        assignment_id: str | None = None,
        assignment_step_id: str | None = None,
        audio_enabled: bool = False,
        created_with: str = "cli",
    ) -> SessionContext:
        sid = str(uuid.uuid4())
        ctx = SessionContext(
            session_id=sid,
            topic_id=topic_id,
            user_stance=user_stance,
            phase=phase,
            max_discussion_turns=max_discussion_turns,
            provider_name=provider_name,
            model_name=model_name,
            snapshot_dir=snapshot_dir,
            runtime_profile_id=(runtime_profile_id or "default"),
            learner_id=learner_id,
            mode_id=mode_id,
            preset_id=preset_id,
            drill_id=drill_id,
            assessment_template_id=assessment_template_id,
            curriculum_pack_id=curriculum_pack_id,
            assignment_id=assignment_id,
            assignment_step_id=assignment_step_id,
            audio_enabled=audio_enabled,
            metadata={
                "created_with": created_with,
                "created_at": _utc_now(),
            },
        )
        try:
            from app.modes.engines.mode_applier import apply_mode_context

            ctx = apply_mode_context(
                ctx,
                mode_id=mode_id,
                preset_id=preset_id,
                drill_id=drill_id,
                assessment_template_id=assessment_template_id,
            )
        except Exception as exc:
            warn_optional_hook_failed(
                "modes.apply_mode_context_on_create",
                exc,
                session_id=sid,
                mode_id=mode_id,
            )
        self.store.save(ctx)
        return ctx

    def load(self, session_id: str) -> SessionContext | None:
        return self.store.load(session_id)

    def save(self, ctx: SessionContext) -> None:
        self.store.save(ctx)
