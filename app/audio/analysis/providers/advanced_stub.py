"""Placeholder for future non-local engines; delegates to mock."""

from __future__ import annotations

from typing import Any

from app.audio.analysis.constants import ANALYZER_ADVANCED_STUB
from app.audio.analysis.providers.mock_delivery_analyzer import MockDeliveryAnalyzer
from app.audio.analysis.schemas.packet import SpeechAnalysisPacket
from app.audio.analysis.schemas.report import SessionSpeechReport


class AdvancedStubAnalyzer(MockDeliveryAnalyzer):
    name = ANALYZER_ADVANCED_STUB

    def analyze_turn(
        self,
        *,
        session_id: str | None,
        turn_id: str | None,
        asset_id: str | None,
        audio_bytes: bytes | None,
        transcript_text: str,
        asr_confidence: float | None,
        speech_cfg: dict[str, Any],
    ) -> SpeechAnalysisPacket:
        p = super().analyze_turn(
            session_id=session_id,
            turn_id=turn_id,
            asset_id=asset_id,
            audio_bytes=audio_bytes,
            transcript_text=transcript_text,
            asr_confidence=asr_confidence,
            speech_cfg=speech_cfg,
        )
        p.metadata = {**p.metadata, "stub": True, "engine": self.name}
        return p

    def analyze_session(
        self,
        *,
        session_id: str,
        turn_packets: list[SpeechAnalysisPacket],
        speech_cfg: dict[str, Any],
    ) -> SessionSpeechReport:
        r = super().analyze_session(session_id=session_id, turn_packets=turn_packets, speech_cfg=speech_cfg)
        r.metadata = {**r.metadata, "stub": True}
        return r
