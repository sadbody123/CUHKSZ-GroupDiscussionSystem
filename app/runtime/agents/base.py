"""Agent execution helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from app.runtime.enums import RoleType
from app.runtime.schemas.transcript import TranscriptTurn
from app.runtime.llm.base import BaseLLMProvider
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.render.prompt_renderer import render_prompt_for_role
from app.runtime.retrieval.router import RoleRouter
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.llm import GenerationRequest, LLMMessage
from app.runtime.schemas.session import SessionContext
from app.runtime.execution.reply_postprocessor import postprocess_reply


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_agent_turn(
    *,
    router: RoleRouter,
    provider: BaseLLMProvider,
    role: str,
    session: SessionContext,
    feedback_packet: dict | None = None,
    participant_context: dict | None = None,
) -> AgentReply:
    prof = resolve_runtime_profile(session.runtime_profile_id)
    signals = None
    if feedback_packet:
        signals = feedback_packet.get("detected_signals")
    pkt = router.build_context_packet(
        role=role,
        topic_id=session.topic_id,
        session_phase=session.phase,
        recent_turns=session.turns,
        user_stance=session.user_stance,
        feedback_signals=signals if role.lower() == RoleType.COACH.value else None,
        retrieval=dict(prof.retrieval),
        participant_context=participant_context,
        context_mode=getattr(session, "agent_context_mode", "swap") or "swap",
        session_participants=list(session.participants or []),
    )
    fb_json = json.dumps(feedback_packet, ensure_ascii=False) if feedback_packet else None
    rp = render_prompt_for_role(
        role=role,
        packet=pkt,
        recent_turns=session.turns,
        user_stance=session.user_stance,
        feedback_packet_json=fb_json,
    )
    req = GenerationRequest(
        provider_name=session.provider_name,
        model=session.model_name,
        messages=[LLMMessage(role="user", content=rp.user_prompt)],
        metadata={"role": role},
    )
    gen = provider.generate(req)
    by = (prof.prompting.get("max_reply_chars_by_role") or {})
    r = role.lower().strip()
    raw = by.get(r, by.get(role))
    max_chars = int(raw) if raw is not None else None

    participant_names: list[str] = []
    current_pid = (participant_context or {}).get("participant_id", "")
    for p in session.participants or []:
        pid = str(p.get("participant_id", ""))
        ctrl = str(p.get("controller_type", "")).lower()
        if ctrl != "user" and pid != current_pid:
            participant_names.append(str(p.get("display_name", pid)))

    from app.runtime.enums import RoleType as RT

    for rt in (RT.USER, RT.MODERATOR, RT.ALLY, RT.OPPONENT, RT.COACH):
        if rt.value.lower() != r:
            participant_names.append(rt.value)

    out_text = postprocess_reply(gen.text, max_chars=max_chars, current_role=role, participant_names=participant_names)
    return AgentReply(
        role=role,
        text=out_text,
        rendered_prompt_id=rp.template_id,
        used_pedagogy_item_ids=list(dict.fromkeys(pkt.used_pedagogy_item_ids)),
        used_evidence_ids=list(dict.fromkeys(pkt.used_evidence_ids)),
        metadata={"provider": gen.provider_name, "model": gen.model},
    )


def append_ai_turn(
    session: SessionContext,
    role: str,
    text: str,
    *,
    input_mode: str = "text",
    tts_asset_id: str | None = None,
    extra_metadata: dict | None = None,
    participant_id: str | None = None,
    team_id: str | None = None,
    speaker_display_name: str | None = None,
    turn_relation_to_user: str | None = None,
    turn_role_type: str | None = None,
) -> None:
    tid = f"{role}-{len(session.turns)+1}"
    meta = {"agent": True, "phase": session.phase, **(extra_metadata or {})}
    session.turns.append(
        TranscriptTurn(
            turn_id=tid,
            speaker_role=role,
            text=text,
            created_at=_utc_now(),
            input_mode=input_mode,
            tts_asset_id=tts_asset_id,
            metadata=meta,
            participant_id=participant_id,
            team_id=team_id,
            speaker_display_name=speaker_display_name,
            turn_relation_to_user=turn_relation_to_user,
            turn_role_type=turn_role_type,
        )
    )
