"""Speech delivery proxy analysis endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_speech_analysis_service
from app.api.schemas.speech import SessionSpeechReportResponse, SpeechAnalysisResponse
from app.application.speech_analysis_service import SpeechAnalysisService

router = APIRouter(tags=["speech"])


@router.post("/sessions/{session_id}/turns/{turn_id}/speech/analyze", response_model=SpeechAnalysisResponse)
def analyze_turn_speech(
    session_id: str,
    turn_id: str,
    svc: Annotated[SpeechAnalysisService, Depends(get_speech_analysis_service)],
    profile_id: str | None = Query(None),
) -> SpeechAnalysisResponse:
    try:
        data = svc.analyze_turn_audio(session_id, turn_id, profile_id=profile_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SpeechAnalysisResponse(analysis=data, proxy_note=data.get("proxy_disclaimer", ""))


@router.post("/sessions/{session_id}/speech/analyze", response_model=SessionSpeechReportResponse)
def analyze_session_speech(
    session_id: str,
    svc: Annotated[SpeechAnalysisService, Depends(get_speech_analysis_service)],
    profile_id: str | None = Query(None),
) -> SessionSpeechReportResponse:
    try:
        data = svc.analyze_session_speech(session_id, profile_id=profile_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SessionSpeechReportResponse(report=data, proxy_note=data.get("proxy_disclaimer", ""))


@router.get("/sessions/{session_id}/speech-report", response_model=SessionSpeechReportResponse)
def get_speech_report(
    session_id: str,
    svc: Annotated[SpeechAnalysisService, Depends(get_speech_analysis_service)],
) -> SessionSpeechReportResponse:
    data = svc.get_session_speech_report(session_id)
    if not data:
        return SessionSpeechReportResponse(report=None, proxy_note="No report stored yet.")
    return SessionSpeechReportResponse(report=data, proxy_note=data.get("proxy_disclaimer", ""))
