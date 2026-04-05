"""Session CRUD and export."""

from __future__ import annotations

from datetime import datetime, timezone

from app.application.config import AppConfig
from app.application.exceptions import SessionNotFoundError
from app.application.snapshot_service import SnapshotService
from app.runtime.schemas.session import SessionContext
from app.runtime.session.file_store import FileSessionStore
from app.runtime.session.manager import SessionManager


class SessionService:
    def __init__(self, config: AppConfig, manager: SessionManager | None = None) -> None:
        self._config = config
        store = FileSessionStore(config.session_storage_dir)
        self._manager = manager or SessionManager(store)
        self._snapshots = SnapshotService(config)

    @property
    def manager(self) -> SessionManager:
        return self._manager

    def create_session(
        self,
        *,
        snapshot_id: str,
        topic_id: str,
        user_stance: str | None,
        provider_name: str | None = None,
        model_name: str | None = None,
        max_discussion_turns: int | None = None,
        runtime_profile_id: str | None = None,
        learner_id: str | None = None,
        mode_id: str | None = None,
        preset_id: str | None = None,
        drill_id: str | None = None,
        assessment_template_id: str | None = None,
        roster_template_id: str | None = None,
        user_participant_id: str | None = None,
        participant_name_overrides: dict | None = None,
        curriculum_pack_id: str | None = None,
        assignment_id: str | None = None,
        assignment_step_id: str | None = None,
        audio_enabled: bool = False,
        source: str = "api",
    ) -> SessionContext:
        path = self._snapshots.resolve_snapshot_dir(snapshot_id)
        roster_id = roster_template_id
        if self._config.enable_group_sim and not roster_id and assessment_template_id:
            from app.application.group_service import GroupService

            roster_id = GroupService(self._config, self).map_assessment_template_to_roster(assessment_template_id)
        ctx = self._manager.create_session(
            topic_id=topic_id,
            snapshot_dir=str(path),
            user_stance=user_stance,
            provider_name=provider_name or self._config.default_provider,
            model_name=model_name if model_name is not None else self._config.default_model,
            max_discussion_turns=max_discussion_turns,
            runtime_profile_id=runtime_profile_id or "default",
            learner_id=learner_id,
            mode_id=mode_id,
            preset_id=preset_id,
            drill_id=drill_id,
            assessment_template_id=assessment_template_id,
            curriculum_pack_id=curriculum_pack_id,
            assignment_id=assignment_id,
            assignment_step_id=assignment_step_id,
            audio_enabled=audio_enabled,
            phase="discussion",
            created_with=source,
        )
        if self._config.enable_group_sim and roster_id:
            from app.application.group_service import GroupService

            uid = user_participant_id or "for_a"
            ctx = GroupService(self._config, self).apply_roster_to_session(
                ctx,
                roster_template_id=roster_id,
                user_participant_id=uid,
                participant_name_overrides=participant_name_overrides,
            )
        return ctx

    def get_session(self, session_id: str) -> SessionContext:
        ctx = self._manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        return ctx

    def list_session_summaries(self) -> list[dict]:
        ids = self._manager.store.list_session_ids()
        out: list[dict] = []
        for sid in ids:
            ctx = self._manager.load(sid)
            if not ctx:
                continue
            out.append(
                {
                    "session_id": ctx.session_id,
                    "topic_id": ctx.topic_id,
                    "phase": ctx.phase,
                    "turn_count": len(ctx.turns),
                    "provider_name": ctx.provider_name,
                    "learner_id": ctx.learner_id,
                }
            )
        return out

    def export_session_dict(self, session_id: str) -> dict:
        ctx = self.get_session(session_id)
        return ctx.model_dump()
