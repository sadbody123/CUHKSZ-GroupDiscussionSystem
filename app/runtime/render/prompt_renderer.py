"""Simple placeholder-based prompt rendering."""

from __future__ import annotations

from app.runtime.prompt_loader import load_prompt_text, prompt_template_id_for_role
from app.runtime.render.packet_serializer import summarize_evidence, summarize_pedagogy, summarize_topic_card
from app.runtime.render.transcript_window import format_transcript_window
from app.runtime.schemas.agent import RenderedPrompt
from app.runtime.schemas.context_packet import RoleContextPacket
from app.runtime.schemas.transcript import TranscriptTurn


def _replace(template: str, mapping: dict[str, str]) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def render_prompt_for_role(
    *,
    role: str,
    packet: RoleContextPacket,
    recent_turns: list[TranscriptTurn],
    user_stance: str | None = None,
    feedback_packet_json: str | None = None,
) -> RenderedPrompt:
    tid = packet.prompt_template_id or prompt_template_id_for_role(role)
    template = load_prompt_text(tid) or f"# {role}\n\n{{USER_PROMPT}}"
    mapping = {
        "TOPIC_CARD": summarize_topic_card(packet.topic_card),
        "PEDAGOGY": summarize_pedagogy(packet.pedagogy_items),
        "EVIDENCE": summarize_evidence(packet.evidence_items),
        "TRANSCRIPT_WINDOW": format_transcript_window(recent_turns),
        "PHASE": packet.session_phase,
        "USER_STANCE": user_stance or "(not specified)",
        "FEEDBACK_PACKET": feedback_packet_json or "(none)",
        "ROLE": role,
        "PARTICIPANT_NAME": packet.participant_display_name or packet.metadata.get("participant_display_name") or "(participant)",
        "SEAT_LABEL": packet.seat_label or "",
        "TEAM_ID": packet.team_id or "",
        "RELATION_TO_USER": packet.relation_to_user or "",
        "PARTICIPANT_MEMORY": packet.participant_memory_summary or "",
        "TEAM_MEMORY": packet.team_memory_summary or "",
        "ROSTER_CONTEXT": packet.roster_context_summary or "",
    }
    body = _replace(template, mapping)
    default_user_prompt = _replace(
        "You are role={{ROLE}} (seat {{SEAT_LABEL}}, team {{TEAM_ID}}, relation={{RELATION_TO_USER}}). "
        "You are speaking as: {{PARTICIPANT_NAME}}. Phase={{PHASE}}. User stance={{USER_STANCE}}.\n"
        "Roster context: {{ROSTER_CONTEXT}}\n"
        "Participant memory: {{PARTICIPANT_MEMORY}}\nTeam hints: {{TEAM_MEMORY}}\n\n"
        "Context:\n{{TOPIC_CARD}}\n\nPedagogy:\n{{PEDAGOGY}}\n\nEvidence:\n{{EVIDENCE}}\n\n"
        "Recent discussion:\n{{TRANSCRIPT_WINDOW}}\n\n"
        "Feedback signals (coach only):\n{{FEEDBACK_PACKET}}\n",
        mapping,
    )
    # If the template file has no {{placeholders}}, prepend its static text to the
    # structured default so instructions plus context are both present.
    if "{{" in template:
        user_prompt = body if "{{" not in body else default_user_prompt
    elif body.strip():
        user_prompt = body.strip() + "\n\n---\n\n" + default_user_prompt
    else:
        user_prompt = default_user_prompt
    return RenderedPrompt(
        role=role,
        template_id=tid,
        system_prompt="You are a discussion participant. Stay in character. Be concise.",
        user_prompt=user_prompt,
        metadata={"mapping_keys": list(mapping.keys())},
    )
