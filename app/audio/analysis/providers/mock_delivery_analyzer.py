"""Stable proxy metrics from transcript + byte hash (tests / fixtures)."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from app.audio.analysis.constants import ANALYZER_MOCK_DELIVERY, DEFAULT_PROXY_DISCLAIMER
from app.audio.analysis.providers.base import BaseSpeechDeliveryAnalyzer
from app.audio.analysis.schemas.packet import SpeechAnalysisPacket
from app.audio.analysis.schemas.report import SessionSpeechReport
from app.audio.analysis.scoring.session_aggregator import aggregate_turn_metrics


class MockDeliveryAnalyzer(BaseSpeechDeliveryAnalyzer):
    name = ANALYZER_MOCK_DELIVERY

    def __init__(self, manifest_path: Path | None = None) -> None:
        self._manifest: dict[str, Any] = {}
        p = manifest_path
        if p and p.is_file():
            self._manifest = json.loads(p.read_text(encoding="utf-8"))

    def _stable(self, audio_bytes: bytes | None, text: str) -> dict[str, float]:
        h = hashlib.sha256((audio_bytes or b"") + text.encode("utf-8")).hexdigest()
        seed = int(h[:8], 16)
        return {
            "pause_ratio": round(0.15 + (seed % 40) / 200, 4),
            "words_per_minute": float(90 + (seed % 80)),
            "pronunciation_proxy_score": round(0.55 + (seed % 35) / 100, 4),
            "fluency_proxy_score": round(0.6 + (seed % 30) / 100, 4),
            "delivery_proxy_score": round(0.58 + (seed % 32) / 100, 4),
        }

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
        ov = self._manifest.get("turn_overrides", {}).get(str(turn_id))
        if isinstance(ov, dict):
            metrics = dict(ov)
        else:
            st = self._stable(audio_bytes, transcript_text)
            wc = len(transcript_text.split())
            metrics = {
                **st,
                "transcript_word_count": wc,
                "duration_ms": 2000 + (hash(transcript_text) % 3000),
                "filler_count": transcript_text.lower().count("um"),
            }
        aid = str(uuid.uuid4())
        return SpeechAnalysisPacket(
            analysis_id=aid,
            session_id=session_id,
            turn_id=turn_id,
            asset_id=asset_id,
            metrics=metrics,
            signals=[
                {
                    "signal_id": "mock_signal",
                    "signal_type": "info",
                    "severity": "low",
                    "message": "Mock delivery analyzer (deterministic hash-based proxy).",
                }
            ],
            strengths=["Mock: stable delivery proxy for tests."],
            risks=[],
            proxy_disclaimer=DEFAULT_PROXY_DISCLAIMER,
            metadata={"analyzer": self.name},
        )

    def analyze_session(
        self,
        *,
        session_id: str,
        turn_packets: list[SpeechAnalysisPacket],
        speech_cfg: dict[str, Any],
    ) -> SessionSpeechReport:
        pdicts = [p.model_dump() for p in turn_packets]
        agg = aggregate_turn_metrics(pdicts)
        return SessionSpeechReport(
            report_id=str(uuid.uuid4()),
            session_id=session_id,
            turn_analysis_ids=[p.analysis_id for p in turn_packets],
            aggregate_metrics=agg,
            signals=[],
            strengths=["Mock session aggregation."],
            risks=[],
            recommended_actions=[],
            proxy_disclaimer=DEFAULT_PROXY_DISCLAIMER,
            metadata={"analyzer": self.name},
        )
