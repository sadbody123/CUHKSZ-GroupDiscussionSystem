"""Orchestrate speech proxy analysis with audio assets and sessions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.session_service import SessionService
from app.audio.analysis.analyzer_factory import get_speech_analyzer
from app.audio.analysis.config import resolve_speech_config
from app.audio.analysis.constants import DEFAULT_PROXY_DISCLAIMER
from app.audio.analysis.pipeline.report_store import SpeechReportStore
from app.audio.pipeline.audio_store import AudioStore
from app.ops.artifacts.registry import ArtifactRegistry
class SpeechAnalysisService:
    def __init__(self, config: AppConfig, session_service: SessionService) -> None:
        self._config = config
        self._sessions = session_service
        self._audio = AudioStore(config.audio_storage_dir)
        self._reports = SpeechReportStore(config.speech_report_dir)

    def analyze_turn_audio(
        self,
        session_id: str,
        turn_id: str,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        cfg = resolve_speech_config(profile_id=profile_id or self._default_profile())
        if not self._config.enable_speech_analysis:
            raise ValueError("speech analysis disabled")
        if not cfg.get("enabled", False):
            raise ValueError("speech analysis disabled in profile")
        ctx = self._sessions.get_session(session_id)
        turn = next((t for t in ctx.turns if t.turn_id == turn_id), None)
        if not turn:
            raise ValueError(f"turn not found: {turn_id}")
        if not turn.audio_asset_id:
            raise ValueError("turn has no user audio asset")
        got = self._audio.read_bytes(turn.audio_asset_id)
        if not got:
            raise ValueError("audio asset missing")
        audio_bytes, _rec = got
        asr_conf = None
        if turn.metadata:
            asr_conf = turn.metadata.get("asr_confidence")
            if asr_conf is not None:
                asr_conf = float(asr_conf)
        an = get_speech_analyzer(cfg.get("analyzer_name"))
        pkt = an.analyze_turn(
            session_id=session_id,
            turn_id=turn_id,
            asset_id=turn.audio_asset_id,
            audio_bytes=audio_bytes,
            transcript_text=turn.text,
            asr_confidence=asr_conf,
            speech_cfg=cfg,
        )
        self._reports.save_turn_packet(session_id, turn_id, pkt)
        ctx = self._sessions.manager.load(session_id)
        if ctx:
            for t in ctx.turns:
                if t.turn_id == turn_id:
                    t.speech_analysis_id = pkt.analysis_id
                    break
            self._sessions.manager.save(ctx)
        ArtifactRegistry().register_artifact(
            self._reports.session_dir(session_id) / f"turn_{turn_id}.json",
            "speech_analysis_report",
            metadata={"analysis_id": pkt.analysis_id},
        )
        return pkt.model_dump()

    def analyze_session_speech(
        self,
        session_id: str,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        cfg = resolve_speech_config(profile_id=profile_id or self._default_profile())
        if not self._config.enable_speech_analysis:
            raise ValueError("speech analysis disabled")
        if not cfg.get("enabled", False):
            raise ValueError("speech analysis disabled in profile")
        ctx = self._sessions.get_session(session_id)
        max_n = int(cfg.get("max_turn_audio_analyze_count", 32))
        an = get_speech_analyzer(cfg.get("analyzer_name"))
        packets: list[Any] = []
        from app.audio.analysis.schemas.packet import SpeechAnalysisPacket

        n = 0
        for t in ctx.turns:
            if n >= max_n:
                break
            if not t.audio_asset_id:
                continue
            got = self._audio.read_bytes(t.audio_asset_id)
            if not got:
                continue
            audio_bytes, _ = got
            asr_conf = t.metadata.get("asr_confidence") if t.metadata else None
            if asr_conf is not None:
                asr_conf = float(asr_conf)
            p = an.analyze_turn(
                session_id=session_id,
                turn_id=t.turn_id,
                asset_id=t.audio_asset_id,
                audio_bytes=audio_bytes,
                transcript_text=t.text,
                asr_confidence=asr_conf,
                speech_cfg=cfg,
            )
            self._reports.save_turn_packet(session_id, t.turn_id, p)
            packets.append(p)
            n += 1
        rep = an.analyze_session(session_id=session_id, turn_packets=packets, speech_cfg=cfg)
        self._reports.save_session_report(session_id, rep)
        ctx2 = self._sessions.manager.load(session_id)
        if ctx2:
            ctx2.speech_report_id = rep.report_id
            ctx2.speech_analysis_enabled = True
            self._sessions.manager.save(ctx2)
        ArtifactRegistry().register_artifact(
            self._reports.session_dir(session_id) / "session_report.json",
            "speech_analysis_report",
            metadata={"report_id": rep.report_id},
        )
        return rep.model_dump()

    def get_turn_speech_analysis(self, session_id: str, turn_id: str) -> dict[str, Any] | None:
        p = self._reports.load_turn_packet(session_id, turn_id)
        return p.model_dump() if p else None

    def get_session_speech_report(self, session_id: str) -> dict[str, Any] | None:
        r = self._reports.load_session_report(session_id)
        return r.model_dump() if r else None

    def _default_profile(self) -> str:
        return get_app_config().default_runtime_profile
