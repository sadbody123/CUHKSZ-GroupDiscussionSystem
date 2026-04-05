"""Execute user / agent turns."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.application.config import get_app_config
from app.integration_logging import warn_optional_hook_failed
from app.group_sim.engines.turn_allocator import NextSpeakerPlan, allocate_next_speaker
from app.runtime.agents.base import append_ai_turn, run_agent_turn
from app.runtime.enums import RoleType
from app.runtime.llm.manager import get_provider
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn
from app.runtime.snapshot_loader import SnapshotBundle, load_snapshot


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_participant(session: SessionContext, pid: str | None) -> dict | None:
    if not pid or not session.participants:
        return None
    for p in session.participants:
        if str(p.get("participant_id")) == pid:
            return p
    return None


class TurnExecutor:
    def __init__(self, bundle: SnapshotBundle, session: SessionContext) -> None:
        self.bundle = bundle
        self.session = session
        ped, top, ev, doc, _src = build_repositories(bundle)
        self.router = RoleRouter(ped, top, ev, doc, snapshot_dir=bundle.path)
        self.profile = resolve_runtime_profile(session.runtime_profile_id)
        self.sm = SessionStateMachine(self.router, orchestration=dict(self.profile.orchestration))
        self.provider = get_provider(session.provider_name)

    @classmethod
    def from_paths(cls, snapshot_dir: Path, session: SessionContext) -> TurnExecutor:
        b = load_snapshot(snapshot_dir.resolve())
        return cls(b, session)

    def _legacy_plan(self, next_role: str) -> NextSpeakerPlan:
        return NextSpeakerPlan(
            next_role=next_role,
            participant_id="",
            team_id=None,
            display_name="",
            seat_label="",
            relation_to_user="",
            turn_role_type="agent",
            allocation_reason="legacy_state_machine",
            candidate_participant_ids=[],
        )

    def _resolve_next_plan(self, last_role: str | None) -> NextSpeakerPlan:
        cfg = get_app_config()
        if cfg.enable_group_sim and self.session.participants:
            plan = allocate_next_speaker(self.session, last_role)
            if plan is not None:
                self.session.next_candidate_participant_ids = plan.candidate_participant_ids
                return plan
        nr = self.sm.peek_next_role(self.session, last_role)
        return self._legacy_plan(nr)

    def _participant_context_for_plan(self, plan: "NextSpeakerPlan") -> dict | None:
        if not plan.participant_id:
            return None
        from app.group_sim.engines.participant_memory import memory_summary_for_prompt
        from app.group_sim.engines.team_coordination import coordination_hint, team_memory_summary

        session = self.session
        uid = session.user_participant_id
        user_team = None
        up = _find_participant(session, uid)
        if up:
            user_team = str(up.get("team_id") or "")
        tm = (
            team_memory_summary(plan.team_id or "", list(session.participants or []), user_team_id=user_team)
            if plan.team_id
            else ""
        )
        mem = memory_summary_for_prompt(session, plan.participant_id)
        ch = coordination_hint(
            speaker_team=plan.team_id,
            user_team_id=user_team,
            phase=session.phase or "",
        )
        roster_bits = [f"{p.get('seat_label')}:{p.get('participant_id')}" for p in (session.participants or [])]
        return {
            "participant_id": plan.participant_id,
            "display_name": plan.display_name,
            "seat_label": plan.seat_label,
            "team_id": plan.team_id,
            "relation_to_user": plan.relation_to_user,
            "participant_memory_summary": mem,
            "team_memory_summary": tm,
            "roster_context_summary": " | ".join(roster_bits) + " | " + ch,
        }

    def submit_user_turn(
        self,
        text: str,
        *,
        input_mode: str = "text",
        audio_asset_id: str | None = None,
        transcript_source: str | None = None,
        tts_asset_id: str | None = None,
        extra_metadata: dict | None = None,
    ) -> SessionContext:
        tid = f"user-{len(self.session.turns)+1}"
        meta = dict(extra_metadata or {})
        uid = self.session.user_participant_id
        up = _find_participant(self.session, uid)
        pid = uid
        team_id = str(up.get("team_id") or "") if up else None
        disp = str(up.get("display_name") or "You") if up else None
        rel = "self"
        trt = "user"
        self.session.turns.append(
            TranscriptTurn(
                turn_id=tid,
                speaker_role=RoleType.USER.value,
                text=text,
                created_at=_utc_now(),
                input_mode=input_mode,
                audio_asset_id=audio_asset_id,
                transcript_source=transcript_source,
                tts_asset_id=tts_asset_id,
                metadata={**meta, "phase": self.session.phase},
                participant_id=pid,
                team_id=team_id,
                speaker_display_name=disp,
                turn_relation_to_user=rel,
                turn_role_type=trt,
            )
        )
        if pid and get_app_config().enable_group_sim:
            try:
                from app.group_sim.engines.participant_memory import record_turn

                record_turn(
                    self.session,
                    participant_id=pid,
                    turn_id=tid,
                    phase=str(self.session.phase or ""),
                    text=text,
                )
            except Exception as exc:
                warn_optional_hook_failed(
                    "group_sim.record_turn_after_user",
                    exc,
                    session_id=self.session.session_id,
                    participant_id=pid,
                )
        return self.session

    def run_next_turn(self) -> tuple[SessionContext, AgentReply | None]:
        last = self.session.turns[-1].speaker_role if self.session.turns else None
        plan = self._resolve_next_plan(last)
        if plan.next_role == RoleType.USER.value:
            return self.session, None
        pctx = self._participant_context_for_plan(plan) if plan.participant_id else None
        reply = run_agent_turn(
            router=self.router,
            provider=self.provider,
            role=plan.next_role,
            session=self.session,
            participant_context=pctx,
        )
        extra: dict = {}
        if plan.participant_id:
            extra["participant_id"] = plan.participant_id
        append_ai_turn(
            self.session,
            plan.next_role,
            reply.text,
            participant_id=plan.participant_id or None,
            team_id=plan.team_id,
            speaker_display_name=plan.display_name or None,
            turn_relation_to_user=plan.relation_to_user or None,
            turn_role_type=plan.turn_role_type or None,
            extra_metadata=extra,
        )
        if plan.participant_id and get_app_config().enable_group_sim:
            try:
                from app.group_sim.engines.participant_memory import record_turn

                lt = self.session.turns[-1]
                record_turn(
                    self.session,
                    participant_id=plan.participant_id,
                    turn_id=lt.turn_id,
                    phase=str(self.session.phase or ""),
                    text=reply.text,
                )
            except Exception as exc:
                warn_optional_hook_failed(
                    "group_sim.record_turn_after_agent",
                    exc,
                    session_id=self.session.session_id,
                    participant_id=plan.participant_id,
                )
        return self.session, reply
