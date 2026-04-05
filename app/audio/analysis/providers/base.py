"""Speech delivery analyzer protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.audio.analysis.schemas.packet import SpeechAnalysisPacket
from app.audio.analysis.schemas.report import SessionSpeechReport


class BaseSpeechDeliveryAnalyzer(ABC):
    name: str = "base"

    @abstractmethod
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
        pass

    @abstractmethod
    def analyze_session(
        self,
        *,
        session_id: str,
        turn_packets: list[SpeechAnalysisPacket],
        speech_cfg: dict[str, Any],
    ) -> SessionSpeechReport:
        pass
