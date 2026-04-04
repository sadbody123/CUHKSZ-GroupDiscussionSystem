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
    out_text = postprocess_reply(gen.text, max_chars=max_chars)
    return AgentReply(
        role=role,
        text=out_text,
        rendered_prompt_id=rp.template_id,
        used_pedagogy_item_ids=list(dict.fromkeys(pkt.used_pedagogy_item_ids)),
        used_evidence_ids=list(dict.fromkeys(pkt.used_evidence_ids)),
        metadata={"provider": gen.provider_name, "model": gen.model},
    )


def append_ai_turn(session: SessionContext, role: str, text: str) -> None:
    tid = f"{role}-{len(session.turns)+1}"
    session.turns.append(
        TranscriptTurn(
            turn_id=tid,
            speaker_role=role,
            text=text,
            created_at=_utc_now(),
            metadata={"agent": True},
        )
    )
