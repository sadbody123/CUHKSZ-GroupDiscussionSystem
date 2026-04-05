"""Group simulation orchestration (roster, balance reports)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.session_service import SessionService
from app.integration_logging import warn_optional_hook_failed
from app.group_sim.constants import ASSESSMENT_TO_ROSTER, GROUP_PRACTICE_NOTE
from app.group_sim.engines.group_report_builder import build_group_balance_report
from app.group_sim.engines.participant_memory import memory_summary_for_prompt
from app.group_sim.engines.roster_resolver import build_participants_and_teams, default_seat_policies
from app.group_sim.loaders.yaml_loader import get_roster_registry
from app.group_sim.schemas.report import GroupBalanceReport
from app.group_sim.store.group_report_store import GroupReportStore
from app.runtime.schemas.session import SessionContext


class GroupService:
    def __init__(self, config: AppConfig | None = None, session_service: SessionService | None = None) -> None:
        self._config = config or get_app_config()
        self._sessions = session_service or SessionService(self._config)
        self._reports = GroupReportStore(self._config.group_reports_dir)

    def list_roster_templates(self) -> list[dict[str, Any]]:
        reg = get_roster_registry()
        out: list[dict[str, Any]] = []
        for rid in reg.list_ids():
            t = reg.get(rid)
            if t:
                out.append(
                    {
                        "roster_template_id": t.roster_template_id,
                        "display_name": t.display_name,
                        "total_participants": t.total_participants,
                        "team_count": t.team_count,
                    }
                )
        return out

    def get_roster_template(self, roster_template_id: str) -> dict[str, Any] | None:
        t = get_roster_registry().get(roster_template_id)
        return t.model_dump() if t else None

    def map_assessment_template_to_roster(self, assessment_template_id: str | None) -> str | None:
        if not assessment_template_id:
            return None
        return ASSESSMENT_TO_ROSTER.get(assessment_template_id)

    def materialize_roster(
        self,
        *,
        roster_template_id: str,
        user_participant_id: str,
        participant_name_overrides: dict[str, str] | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
        t = get_roster_registry().get(roster_template_id)
        if not t:
            raise ValueError(f"roster template not found: {roster_template_id}")
        parts, teams = build_participants_and_teams(
            t,
            user_participant_id=user_participant_id,
            participant_name_overrides=participant_name_overrides,
        )
        policies = default_seat_policies(parts)
        return parts, teams, policies

    def build_session_roster(
        self,
        *,
        roster_template_id: str,
        user_participant_id: str,
        participant_name_overrides: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        parts, teams, policies = self.materialize_roster(
            roster_template_id=roster_template_id,
            user_participant_id=user_participant_id,
            participant_name_overrides=participant_name_overrides,
        )
        return {"participants": parts, "teams": teams, "seat_policies": policies}

    def apply_roster_to_session(
        self,
        ctx: SessionContext,
        *,
        roster_template_id: str | None,
        user_participant_id: str | None,
        participant_name_overrides: dict[str, str] | None = None,
    ) -> SessionContext:
        if not self._config.enable_group_sim or not roster_template_id:
            return ctx
        uid = user_participant_id
        if not uid:
            t = get_roster_registry().get(roster_template_id)
            if t and t.participants:
                uid = str(t.participants[0].get("participant_id") or "")
        if not uid:
            return ctx
        parts, teams, policies = self.materialize_roster(
            roster_template_id=roster_template_id,
            user_participant_id=uid,
            participant_name_overrides=participant_name_overrides,
        )
        ctx.roster_template_id = roster_template_id
        ctx.participants = parts
        ctx.teams = teams
        ctx.user_participant_id = uid
        ctx.seat_policies = policies
        ctx.participant_memory_state = ctx.participant_memory_state or {}
        self._sessions.manager.save(ctx)
        return ctx

    def get_session_roster(self, session_id: str) -> dict[str, Any]:
        ctx = self._sessions.get_session(session_id)
        return {
            "session_id": session_id,
            "roster_template_id": ctx.roster_template_id,
            "user_participant_id": ctx.user_participant_id,
            "participants": list(ctx.participants or []),
            "teams": list(ctx.teams or []),
            "simulation_note": GROUP_PRACTICE_NOTE,
        }

    def get_group_balance(self, session_id: str) -> dict[str, Any]:
        ctx = self._sessions.get_session(session_id)
        ex = self._reports.load_by_session(session_id)
        if ex:
            return ex.model_dump()
        rep = build_group_balance_report(ctx)
        return rep.model_dump()

    def rebuild_group_report(self, session_id: str, *, persist: bool = True) -> GroupBalanceReport:
        ctx = self._sessions.get_session(session_id)
        rep = build_group_balance_report(ctx)
        if persist:
            self._reports.save(rep)
            ctx.group_balance_report_id = rep.report_id
            self._sessions.manager.save(ctx)
            try:
                from app.ops.artifacts.registry import ArtifactRegistry

                ArtifactRegistry().register_artifact(
                    self._config.group_reports_dir / f"{session_id}_{rep.report_id}.json",
                    "group_balance_report",
                    metadata={"session_id": session_id},
                )
            except Exception as exc:
                warn_optional_hook_failed("artifacts.register_group_report", exc, session_id=session_id)
        return rep

    def get_participant_memory_summary(self, session_id: str, participant_id: str) -> str:
        ctx = self._sessions.get_session(session_id)
        return memory_summary_for_prompt(ctx, participant_id)

    def resolve_user_participant_id(self, session_id: str) -> str | None:
        ctx = self._sessions.get_session(session_id)
        return ctx.user_participant_id

    def maybe_auto_group_report(self, session_id: str) -> None:
        if not self._config.auto_generate_group_report or not self._config.enable_group_sim:
            return
        try:
            self.rebuild_group_report(session_id, persist=True)
        except Exception as exc:
            warn_optional_hook_failed("group.maybe_auto_group_report", exc, session_id=session_id)

    def get_group_report_payload(self, session_id: str) -> dict[str, Any]:
        """Combined balance + roster summary for API."""
        roster = self.get_session_roster(session_id)
        bal = self.get_group_balance(session_id)
        return {"roster": roster, "balance": bal, "simulation_note": GROUP_PRACTICE_NOTE}
