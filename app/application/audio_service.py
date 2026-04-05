"""Audio transcription, synthesis, and asset access (phase 9)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.application.exceptions import PhaseConflictError, SessionNotFoundError
from app.audio.constants import (
    ASSET_AGENT_TTS,
    ASSET_COACH_TTS,
    ASSET_USER_UPLOAD,
    INPUT_MODE_AUDIO,
    TRANSCRIPT_ASR,
)
from app.audio.pipeline import AudioStore
from app.audio.pipeline.mime import normalize_audio_mime
from app.audio.pipeline.transcription import transcribe
from app.audio.pipeline.validators import validate_upload_size
from app.audio.pipeline.synthesis import synthesize
from app.audio.providers.manager import get_asr_provider, get_tts_provider
from app.audio.schemas.asr import TranscriptionRequest, TranscriptionResponse
from app.audio.schemas.audio import AudioAssetRecord
from app.audio.schemas.tts import SynthesisRequest
from app.ops.artifacts.registry import ArtifactRegistry
from app.ops.settings import get_ops_settings
from app.runtime.enums import RoleType
from app.runtime.execution.turn_executor import TurnExecutor
from .config import AppConfig
from .session_service import SessionService


class AudioService:
    def __init__(self, config: AppConfig, session_service: SessionService) -> None:
        self._config = config
        self._sessions = session_service
        self._store = AudioStore(config.audio_storage_dir)
        self._ops = get_ops_settings()

    def _registry_note(self, rec: AudioAssetRecord) -> None:
        ArtifactRegistry().register_artifact(Path(rec.file_path), "audio_asset", metadata={"asset_id": rec.asset_id})

    def transcribe_audio_file(
        self,
        *,
        session_id: str | None,
        audio_path: Path | None = None,
        audio_bytes: bytes | None = None,
        file_name: str = "upload.wav",
        mime_type: str | None = None,
        provider_name: str | None = None,
        save_asset: bool = False,
    ) -> tuple[TranscriptionResponse, AudioAssetRecord | None]:
        if not self._config.enable_audio:
            raise ValueError("audio is disabled")
        s = self._ops
        max_b = s.max_audio_upload_mb * 1024 * 1024
        data: bytes
        if audio_path is not None:
            data = audio_path.read_bytes()
            file_name = audio_path.name
        elif audio_bytes is not None:
            data = audio_bytes
        else:
            raise ValueError("audio_path or audio_bytes required")
        validate_upload_size(len(data), max_b)
        prov = get_asr_provider(provider_name or s.default_asr_provider, s)
        req = TranscriptionRequest(
            provider_name=prov.name,
            file_path=str(audio_path) if audio_path else None,
            audio_bytes=data if audio_path is None else None,
            mime_type=normalize_audio_mime(mime_type),
            metadata={},
        )
        resp = transcribe(req, prov)
        rec: AudioAssetRecord | None = None
        if save_asset and session_id:
            rec = self._store.save_bytes(
                session_id=session_id,
                data=data,
                file_name=file_name,
                asset_kind=ASSET_USER_UPLOAD,
                mime_type=normalize_audio_mime(mime_type),
                provider_name=prov.name,
                transcript_text=resp.text,
                extra_meta={"transcription_only": True},
            )
            self._append_session_asset(session_id, rec.asset_id)
            self._registry_note(rec)
        return resp, rec

    def submit_user_audio_turn(
        self,
        session_id: str,
        audio_path: Path,
        *,
        provider_name: str | None = None,
    ) -> dict[str, Any]:
        if not self._config.enable_audio:
            raise ValueError("audio is disabled")
        ctx = self._sessions.manager.load(session_id)
        if not ctx or not ctx.snapshot_dir:
            raise SessionNotFoundError(session_id)
        if ctx.phase == "feedback":
            raise PhaseConflictError("Cannot add user audio turn in feedback phase")
        data = audio_path.read_bytes()
        validate_upload_size(len(data), self._ops.max_audio_upload_mb * 1024 * 1024)
        prov = get_asr_provider(provider_name or self._ops.default_asr_provider, self._ops)
        req = TranscriptionRequest(
            provider_name=prov.name,
            file_path=str(audio_path.resolve()),
            mime_type=normalize_audio_mime(None),
            metadata={},
        )
        resp = transcribe(req, prov)
        rec = self._store.save_bytes(
            session_id=session_id,
            data=data,
            file_name=audio_path.name,
            asset_kind=ASSET_USER_UPLOAD,
            mime_type=normalize_audio_mime(None),
            provider_name=prov.name,
            transcript_text=resp.text,
        )
        self._append_session_asset(session_id, rec.asset_id)
        self._registry_note(rec)
        ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
        ex.submit_user_turn(
            resp.text,
            input_mode=INPUT_MODE_AUDIO,
            audio_asset_id=rec.asset_id,
            transcript_source=TRANSCRIPT_ASR,
        )
        sess = ex.session
        sess.audio_enabled = True
        sess.asr_provider_name = prov.name
        self._sessions.manager.save(sess)
        new_turn = sess.turns[-1].model_dump() if sess.turns else {}
        return {
            "session": sess.model_dump(),
            "created_turn": new_turn,
            "transcription": resp.model_dump(),
            "audio_asset": rec.model_dump(),
        }

    def synthesize_turn_audio(
        self,
        session_id: str,
        turn_id: str,
        *,
        provider_name: str | None = None,
    ) -> AudioAssetRecord:
        if not self._config.enable_audio:
            raise ValueError("audio is disabled")
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        turn = next((t for t in ctx.turns if t.turn_id == turn_id), None)
        if not turn:
            raise ValueError(f"turn not found: {turn_id}")
        role = turn.speaker_role
        prov = get_tts_provider(provider_name or self._ops.default_tts_provider, self._ops)
        req = SynthesisRequest(
            provider_name=prov.name,
            text=turn.text,
            voice=None,
            role=role,
            session_id=session_id,
            turn_id=turn_id,
            metadata={},
        )
        out = synthesize(req, prov)
        kind = ASSET_COACH_TTS if role.lower() == RoleType.COACH.value else ASSET_AGENT_TTS
        rec = self._store.save_bytes(
            session_id=session_id,
            data=out.audio_bytes,
            file_name=f"{turn_id}.wav",
            asset_kind=kind,
            mime_type=out.mime_type,
            provider_name=prov.name,
            turn_id=turn_id,
            extra_meta={"turn_id": turn_id, "role": role},
        )
        turn.tts_asset_id = rec.asset_id
        ctx.tts_provider_name = prov.name
        self._append_session_asset(session_id, rec.asset_id)
        self._sessions.manager.save(ctx)
        self._registry_note(rec)
        return rec

    def synthesize_coach_report_audio(
        self,
        session_id: str,
        *,
        provider_name: str | None = None,
    ) -> AudioAssetRecord | None:
        if not self._config.enable_audio:
            raise ValueError("audio is disabled")
        ctx = self._sessions.manager.load(session_id)
        if not ctx or not ctx.coach_report:
            return None
        text = str(ctx.coach_report.get("text") or "")
        if not text.strip():
            return None
        prov = get_tts_provider(provider_name or self._ops.default_tts_provider, self._ops)
        req = SynthesisRequest(
            provider_name=prov.name,
            text=text,
            voice=None,
            role=RoleType.COACH.value,
            session_id=session_id,
            turn_id=None,
            metadata={"kind": "coach_report"},
        )
        out = synthesize(req, prov)
        rec = self._store.save_bytes(
            session_id=session_id,
            data=out.audio_bytes,
            file_name="coach_report.wav",
            asset_kind=ASSET_COACH_TTS,
            mime_type=out.mime_type,
            provider_name=prov.name,
            extra_meta={"coach_report": True},
        )
        ctx.coach_report = dict(ctx.coach_report)
        ctx.coach_report["tts_asset_id"] = rec.asset_id
        ctx.tts_provider_name = prov.name
        self._append_session_asset(session_id, rec.asset_id)
        self._sessions.manager.save(ctx)
        self._registry_note(rec)
        return rec

    def list_session_audio_assets(self, session_id: str) -> list[AudioAssetRecord]:
        return self._store.list_session_assets(session_id)

    def get_audio_asset(self, asset_id: str) -> tuple[bytes, AudioAssetRecord] | None:
        return self._store.read_bytes(asset_id)

    def export_audio_asset_to_path(self, asset_id: str, output_file: Path) -> AudioAssetRecord:
        got = self._store.read_bytes(asset_id)
        if not got:
            raise ValueError("asset not found")
        data, rec = got
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(data)
        return rec

    def _append_session_asset(self, session_id: str, asset_id: str) -> None:
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            return
        ids = list(ctx.audio_asset_ids or [])
        if asset_id not in ids:
            ids.append(asset_id)
        ctx.audio_asset_ids = ids
        self._sessions.manager.save(ctx)
