"""Sessions: CRUD, turns, auto-run, feedback, export."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.api.deps import (
    get_discussion_service,
    get_feedback_service,
    get_group_service,
    get_learner_service,
    get_mode_service,
    get_session_service,
)
from app.api.schemas.learner import AttachSessionToLearnerRequest, AttachSessionToLearnerResponse
from app.api.schemas.feedback import FeedbackResponse
from app.api.schemas.mode import ModeReportResponse, ModeStatusResponse
from app.api.schemas.group_sim import (
    GroupBalanceResponse,
    GroupReportResponse,
    ParticipantSummaryResponse,
    SessionRosterResponse,
)
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
from app.application.learner_service import LearnerService
from app.application.mode_service import ModeService
from app.application.group_service import GroupService
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
        learner_id=body.learner_id,
        mode_id=body.mode_id,
        preset_id=body.preset_id,
        drill_id=body.drill_id,
        assessment_template_id=body.assessment_template_id,
        roster_template_id=body.roster_template_id,
        user_participant_id=body.user_participant_id,
        participant_name_overrides=body.participant_name_overrides,
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
        learner_id=ctx.learner_id,
        mode_id=ctx.mode_id,
        preset_id=ctx.preset_id,
        drill_id=ctx.drill_id,
        assessment_template_id=ctx.assessment_template_id,
        roster_template_id=ctx.roster_template_id,
        user_participant_id=ctx.user_participant_id,
    )


@router.get("/{session_id}/roster", response_model=SessionRosterResponse)
def session_roster(
    session_id: str,
    gsvc: Annotated[GroupService, Depends(get_group_service)],
) -> SessionRosterResponse:
    try:
        r = gsvc.get_session_roster(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return SessionRosterResponse(**r)


@router.get("/{session_id}/balance", response_model=GroupBalanceResponse)
def session_balance(
    session_id: str,
    gsvc: Annotated[GroupService, Depends(get_group_service)],
) -> GroupBalanceResponse:
    try:
        raw = gsvc.get_group_balance(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return GroupBalanceResponse(**raw)


@router.get("/{session_id}/participants", response_model=list[ParticipantSummaryResponse])
def session_participants(
    session_id: str,
    svc: Annotated[SessionService, Depends(get_session_service)],
) -> list[ParticipantSummaryResponse]:
    try:
        ctx = svc.get_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    parts = list(ctx.participants or [])
    from collections import Counter

    c = Counter()
    for t in ctx.turns:
        pid = getattr(t, "participant_id", None) or (t.metadata or {}).get("participant_id")
        if pid:
            c[str(pid)] += 1
    out: list[ParticipantSummaryResponse] = []
    for p in parts:
        pid = str(p.get("participant_id") or "")
        out.append(
            ParticipantSummaryResponse(
                participant_id=pid,
                display_name=p.get("display_name"),
                team_id=p.get("team_id"),
                relation_to_user=p.get("relation_to_user"),
                turn_count=int(c.get(pid, 0)),
            )
        )
    return out


@router.get("/{session_id}/group-report", response_model=GroupReportResponse)
def session_group_report(
    session_id: str,
    gsvc: Annotated[GroupService, Depends(get_group_service)],
) -> GroupReportResponse:
    try:
        raw = gsvc.get_group_report_payload(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return GroupReportResponse(**raw)


@router.get("/{session_id}", response_model=SessionStatusResponse)
def get_session(
    session_id: str,
    disc: Annotated[DiscussionService, Depends(get_discussion_service)],
) -> SessionStatusResponse:
    st = disc.get_session_status(session_id)
    return SessionStatusResponse(
        session_id=st["session_id"],
        topic_id=st["topic_id"],
        learner_id=st.get("learner_id"),
        mode_id=st.get("mode_id"),
        preset_id=st.get("preset_id"),
        drill_id=st.get("drill_id"),
        assessment_template_id=st.get("assessment_template_id"),
        mode_report_id=st.get("mode_report_id"),
        mode_state=st.get("mode_state") or {},
        timer_state=st.get("timer_state") or {},
        simulation_note=st.get("simulation_note"),
        phase=st["phase"],
        runtime_profile_id=st.get("runtime_profile_id", "default"),
        retrieval_mode=st.get("retrieval_mode", "rule"),
        has_indexes=bool(st.get("has_indexes", False)),
        provider_name=st["provider_name"],
        model_name=st.get("model_name"),
        turn_count=st["turn_count"],
        latest_turns=st["latest_turns"],
        feedback_ready=st["feedback_ready"],
        coach_report_present=st["coach_report_present"],
        coach_text_preview=st.get("coach_text_preview"),
        can_run_next=st["can_run_next"],
        peek_next_role=st.get("peek_next_role"),
        audio_enabled=bool(st.get("audio_enabled", False)),
        asr_provider_name=st.get("asr_provider_name"),
        tts_provider_name=st.get("tts_provider_name"),
        audio_asset_count=int(st.get("audio_asset_count", 0)),
        speech_report_id=st.get("speech_report_id"),
        speech_analysis_enabled=bool(st.get("speech_analysis_enabled", False)),
        roster_template_id=st.get("roster_template_id"),
        user_participant_id=st.get("user_participant_id"),
        participants=list(st.get("participants") or []),
        teams=list(st.get("teams") or []),
        group_balance_report_id=st.get("group_balance_report_id"),
        next_candidate_participant_ids=list(st.get("next_candidate_participant_ids") or []),
        curriculum_pack_id=st.get("curriculum_pack_id"),
        assignment_id=st.get("assignment_id"),
        assignment_step_id=st.get("assignment_step_id"),
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
    with_tts: bool = Query(False),
    tts_provider: str | None = Query(None),
) -> RunNextTurnResponse:
    sess, reply, next_role = disc.run_next_turn(session_id, with_tts=with_tts, tts_provider=tts_provider)
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
    svc: Annotated[SessionService, Depends(get_session_service)],
    with_tts: bool = Query(False),
    tts_provider: str | None = Query(None),
    with_speech_analysis: bool = Query(False),
    speech_profile_id: str | None = Query(None),
) -> FeedbackResponse:
    report = fb.generate_feedback(
        session_id,
        with_tts=with_tts,
        tts_provider=tts_provider,
        with_speech_analysis=with_speech_analysis,
        speech_profile_id=speech_profile_id,
    )
    ctx = svc.get_session(session_id)
    tts_aid = None
    if ctx.coach_report and isinstance(ctx.coach_report, dict):
        tts_aid = ctx.coach_report.get("tts_asset_id")
    return FeedbackResponse(
        session_id=report.session_id,
        topic_id=report.topic_id,
        coach_text=report.text,
        strengths=list(report.strengths),
        risks=list(report.risks),
        suggested_next_actions=list(report.suggested_next_actions),
        feedback_packet=dict(report.feedback_packet),
        metadata=dict(report.metadata),
        coach_tts_asset_id=tts_aid,
        speech_report=report.speech_report,
        speech_proxy_disclaimer=(
            report.feedback_packet.get("speech_proxy_disclaimer")
            if isinstance(report.feedback_packet, dict)
            else None
        ),
        speech_strengths=list(report.speech_strengths),
        speech_risks=list(report.speech_risks),
        proxy_limitations=list(report.proxy_limitations),
    )


@router.get("/{session_id}/mode-status", response_model=ModeStatusResponse)
def session_mode_status(
    session_id: str,
    msvc: Annotated[ModeService, Depends(get_mode_service)],
) -> ModeStatusResponse:
    try:
        st = msvc.get_mode_status(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return ModeStatusResponse(**st)


@router.get("/{session_id}/mode-report", response_model=ModeReportResponse)
def session_mode_report(
    session_id: str,
    msvc: Annotated[ModeService, Depends(get_mode_service)],
) -> ModeReportResponse:
    try:
        rep = msvc.load_or_build_mode_report(session_id, persist_if_built=False)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return ModeReportResponse(**rep.model_dump())


@router.post("/{session_id}/attach-learner", response_model=AttachSessionToLearnerResponse)
def attach_session_to_learner(
    session_id: str,
    body: AttachSessionToLearnerRequest,
    lsvc: Annotated[LearnerService, Depends(get_learner_service)],
) -> AttachSessionToLearnerResponse:
    try:
        r = lsvc.attach_session_to_learner(body.learner_id, session_id, ingest=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return AttachSessionToLearnerResponse(**r)


@router.get("/{session_id}/export")
def export_session(
    session_id: str,
    svc: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    data = svc.export_session_dict(session_id)
    return JSONResponse(content=data)
