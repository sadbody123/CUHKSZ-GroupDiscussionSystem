"""Coach report generation."""

from __future__ import annotations

import json

from app.runtime.agents.base import run_agent_turn
from app.runtime.llm.base import BaseLLMProvider
from app.runtime.retrieval.router import RoleRouter
from app.runtime.schemas.coach_report import CoachReport
from app.runtime.schemas.feedback import FeedbackPacket
from app.runtime.schemas.session import SessionContext


def generate_coach_report(
    *,
    router: RoleRouter,
    provider: BaseLLMProvider,
    session: SessionContext,
    feedback: FeedbackPacket,
) -> CoachReport:
    fb_dict = feedback.model_dump()
    reply = run_agent_turn(
        router=router,
        provider=provider,
        role="coach",
        session=session,
        feedback_packet=fb_dict,
    )
    actions: list[str] = []
    for pid in feedback.recommended_pedagogy_item_ids[:5]:
        actions.append(f"Review pedagogy item {pid}")
    return CoachReport(
        session_id=session.session_id,
        topic_id=session.topic_id,
        text=reply.text,
        strengths=list(feedback.strengths),
        risks=list(feedback.risks),
        suggested_next_actions=actions,
        feedback_packet=fb_dict,
        metadata={"rendered_prompt": reply.rendered_prompt_id, "raw_feedback_json": json.dumps(fb_dict)[:2000]},
    )
