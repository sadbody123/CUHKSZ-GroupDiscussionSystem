"""Sessions: CRUD, turns, auto-run, feedback, export."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_discussion_service, get_feedback_service, get_session_service
from app.api.schemas.feedback import FeedbackResponse
from app.api.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionListItemResponse,
    SessionStatusResponse,
)
from app.api.schemas.turn import (
    AutoRunRequest,
    AutoRunResponse,
    RunNextTurnResponse,
    SubmitUserTurnRequest,
    SubmitUserTurnResponse,
)
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionListItemResponse])
def list_sessions(svc: Annotated[SessionService, Depends(get_session_service)]) -> list[SessionListItemResponse]:
    rows = svc.list_session_summaries()
    return [SessionListItemResponse(**r) for r in rows]


@router.post("", response_model=CreateSessionResponse)
def create_session(
    body: CreateSessionRequest,
    svc: Annotated[SessionService, Depends(get_session_service)],
) -> CreateSessionResponse:
    ctx = svc.create_session(
        snapshot_id=body.snapshot_id,
        topic_id=body.topic_id,
        user_stance=body.user_stance,
        provider_name=body.provider_name,
        model_name=body.model_name,
        max_discussion_turns=body.max_discussion_turns,
        runtime_profile_id=body.runtime_profile_id,
        source="api",
    )
    created_at = str(ctx.metadata.get("created_at", ""))
    return CreateSessionResponse(
        session_id=ctx.session_id,
        phase=ctx.phase,
        topic_id=ctx.topic_id,
        provider_name=ctx.provider_name,
        runtime_profile_id=ctx.runtime_profile_id,
        created_at=created_at,
    )


@router.get("/{session_id}", response_model=SessionStatusResponse)
def get_session(
    session_id: str,
    disc: Annotated[DiscussionService, Depends(get_discussion_service)],
) -> SessionStatusResponse:
    st = disc.get_session_status(session_id)
    return SessionStatusResponse(
        session_id=st["session_id"],
        topic_id=st["topic_id"],
        phase=st["phase"],
        runtime_profile_id=st.get("runtime_profile_id", "default"),
        provider_name=st["provider_name"],
        model_name=st.get("model_name"),
        turn_count=st["turn_count"],
        latest_turns=st["latest_turns"],
        feedback_ready=st["feedback_ready"],
        coach_report_present=st["coach_report_present"],
        coach_text_preview=st.get("coach_text_preview"),
        can_run_next=st["can_run_next"],
        peek_next_role=st.get("peek_next_role"),
    )


@router.post("/{session_id}/turns/user", response_model=SubmitUserTurnResponse)
def submit_user_turn(
    session_id: str,
    body: SubmitUserTurnRequest,
    disc: Annotated[DiscussionService, Depends(get_discussion_service)],
) -> SubmitUserTurnResponse:
    sess = disc.submit_user_turn(session_id, body.text)
    new_turn = sess.turns[-1].model_dump() if sess.turns else {}
    return SubmitUserTurnResponse(
        session_id=sess.session_id,
        turn_count=len(sess.turns),
        new_turn=new_turn,
    )


@router.post("/{session_id}/run-next", response_model=RunNextTurnResponse)
def run_next_turn(
    session_id: str,
    disc: Annotated[DiscussionService, Depends(get_discussion_service)],
) -> RunNextTurnResponse:
    sess, reply, next_role = disc.run_next_turn(session_id)
    return RunNextTurnResponse(
        next_role=next_role,
        generated_reply=reply.text if reply else None,
        generated_role=reply.role if reply else None,
        updated_phase=sess.phase,
        turn_count=len(sess.turns),
        reply_metadata=reply.metadata if reply else {},
    )


@router.post("/{session_id}/auto-run", response_model=AutoRunResponse)
def auto_run(
    session_id: str,
    body: AutoRunRequest,
    disc: Annotated[DiscussionService, Depends(get_discussion_service)],
) -> AutoRunResponse:
    sess, replies = disc.auto_run_discussion(session_id, max_steps=body.max_steps, auto_fill_user=True)
    new_turns: list[dict[str, Any]] = []
    for r in replies:
        new_turns.append({"role": r.role, "text": r.text, "metadata": r.metadata})
    return AutoRunResponse(new_turns=new_turns, session=sess.model_dump())


@router.post("/{session_id}/feedback", response_model=FeedbackResponse)
def generate_feedback(
    session_id: str,
    fb: Annotated[FeedbackService, Depends(get_feedback_service)],
) -> FeedbackResponse:
    report = fb.generate_feedback(session_id)
    return FeedbackResponse(
        session_id=report.session_id,
        topic_id=report.topic_id,
        coach_text=report.text,
        strengths=list(report.strengths),
        risks=list(report.risks),
        suggested_next_actions=list(report.suggested_next_actions),
        feedback_packet=dict(report.feedback_packet),
        metadata=dict(report.metadata),
    )


@router.get("/{session_id}/export")
def export_session(
    session_id: str,
    svc: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    data = svc.export_session_dict(session_id)
    return JSONResponse(content=data)
