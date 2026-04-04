"""Prompt rendering."""

from __future__ import annotations

from app.runtime.render.prompt_renderer import render_prompt_for_role
from app.runtime.schemas.context_packet import RoleContextPacket
from app.runtime.schemas.transcript import TranscriptTurn


def test_renderer_fills_placeholders():
    pkt = RoleContextPacket(
        role="ally",
        topic_id="t1",
        session_phase="discussion",
        topic_card={"topic": "AI", "summary": "test"},
        pedagogy_items=[{"item_id": "p1", "item_type": "rule", "content": "be nice"}],
        evidence_items=[{"evidence_id": "e1", "text": "evidence body"}],
        used_pedagogy_item_ids=["p1"],
        used_evidence_ids=["e1"],
    )
    turns = [TranscriptTurn(turn_id="1", speaker_role="user", text="hi", created_at="")]
    rp = render_prompt_for_role(
        role="ally",
        packet=pkt,
        recent_turns=turns,
        user_stance="for",
    )
    assert "AI" in rp.user_prompt or "discussion" in rp.user_prompt
    assert rp.template_id
