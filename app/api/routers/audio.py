"""Audio: transcribe, submit, TTS, list, download."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.deps import get_audio_service
from app.api.schemas.audio import (
    AudioAssetResponse,
    SessionAudioAssetListResponse,
    SubmitUserAudioResponse,
    SynthesizeTurnAudioResponse,
    TranscribeAudioResponse,
)
from app.application.audio_service import AudioService
from app.application.exceptions import PhaseConflictError, SessionNotFoundError
from app.ops.settings import get_ops_settings

router = APIRouter(tags=["audio"])


def _asset_resp(rec) -> AudioAssetResponse:
    d = rec.model_dump()
    d.pop("file_path", None)
    return AudioAssetResponse(**d)


@router.post("/sessions/{session_id}/audio/user-transcribe", response_model=TranscribeAudioResponse)
async def user_transcribe(
    session_id: str,
    svc: Annotated[AudioService, Depends(get_audio_service)],
    audio: UploadFile = File(...),
    provider_name: str | None = Form(None),
    save_asset: bool = Form(False),
) -> TranscribeAudioResponse:
    s = get_ops_settings()
    raw = await audio.read()
    max_b = s.max_audio_upload_mb * 1024 * 1024
    if len(raw) > max_b:
        raise HTTPException(status_code=413, detail="audio too large")
    try:
        resp, rec = svc.transcribe_audio_file(
            session_id=session_id if save_asset else None,
            audio_bytes=raw,
            file_name=audio.filename or "upload.wav",
            mime_type=audio.content_type,
            provider_name=provider_name,
            save_asset=save_asset,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return TranscribeAudioResponse(
        transcript=resp.text,
        provider_name=resp.provider_name,
        language=resp.language,
        confidence=resp.confidence,
        asset=_asset_resp(rec) if rec else None,
    )


@router.post("/sessions/{session_id}/audio/user-submit", response_model=SubmitUserAudioResponse)
async def user_submit_audio(
    session_id: str,
    svc: Annotated[AudioService, Depends(get_audio_service)],
    audio: UploadFile = File(...),
    provider_name: str | None = Form(None),
) -> SubmitUserAudioResponse:
    s = get_ops_settings()
    raw = await audio.read()
    max_b = s.max_audio_upload_mb * 1024 * 1024
    if len(raw) > max_b:
        raise HTTPException(status_code=413, detail="audio too large")
    suffix = Path(audio.filename or "upload.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(raw)
        tpath = Path(tmp.name)
    try:
        try:
            out = svc.submit_user_audio_turn(session_id, tpath, provider_name=provider_name)
        except SessionNotFoundError as e:
            raise HTTPException(status_code=404, detail="session not found") from e
        except PhaseConflictError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    finally:
        tpath.unlink(missing_ok=True)
    ar = out["audio_asset"]
    if hasattr(ar, "model_dump"):
        ard = ar.model_dump()
    else:
        ard = ar
    return SubmitUserAudioResponse(
        session_id=out["session"]["session_id"],
        turn_count=len(out["session"].get("turns", [])),
        created_turn=out["created_turn"],
        transcription=out["transcription"],
        audio_asset=AudioAssetResponse(**{k: v for k, v in ard.items() if k != "file_path"}),
    )


@router.post("/sessions/{session_id}/turns/{turn_id}/tts", response_model=SynthesizeTurnAudioResponse)
def synthesize_turn_tts(
    session_id: str,
    turn_id: str,
    svc: Annotated[AudioService, Depends(get_audio_service)],
    provider_name: str | None = None,
) -> SynthesizeTurnAudioResponse:
    try:
        rec = svc.synthesize_turn_audio(session_id, turn_id, provider_name=provider_name)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail="session not found") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SynthesizeTurnAudioResponse(
        asset=_asset_resp(rec),
        download_path=f"/audio/{rec.asset_id}",
    )


@router.get("/sessions/{session_id}/audio-assets", response_model=SessionAudioAssetListResponse)
def list_audio_assets(
    session_id: str,
    svc: Annotated[AudioService, Depends(get_audio_service)],
) -> SessionAudioAssetListResponse:
    rows = svc.list_session_audio_assets(session_id)
    return SessionAudioAssetListResponse(
        session_id=session_id,
        assets=[_asset_resp(r) for r in rows],
    )


@router.get("/audio/{asset_id}")
def download_audio(asset_id: str, svc: Annotated[AudioService, Depends(get_audio_service)]) -> Response:
    got = svc.get_audio_asset(asset_id)
    if not got:
        raise HTTPException(status_code=404, detail="not found")
    data, rec = got
    return Response(content=data, media_type=rec.mime_type or "audio/wav")
