"""Deterministic local WAV analysis (stdlib wave + heuristics)."""

from __future__ import annotations

import uuid
from typing import Any

from app.audio.analysis.constants import ANALYZER_LOCAL_WAVE, DEFAULT_PROXY_DISCLAIMER
from app.audio.analysis.pipeline.analyze_asset import analyze_bytes_to_metrics
from app.audio.analysis.providers.base import BaseSpeechDeliveryAnalyzer
from app.audio.analysis.schemas.packet import SpeechAnalysisPacket
from app.audio.analysis.schemas.report import SessionSpeechReport
from app.audio.analysis.scoring.rubric_mapper import rubric_tags_for_signals
from app.audio.analysis.scoring.session_aggregator import aggregate_turn_metrics


class LocalWaveAnalyzer(BaseSpeechDeliveryAnalyzer):
    name = ANALYZER_LOCAL_WAVE

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
        if not audio_bytes:
            return SpeechAnalysisPacket(
                analysis_id=str(uuid.uuid4()),
                session_id=session_id,
                turn_id=turn_id,
                asset_id=asset_id,
                metrics={},
                signals=[
                    {
                        "signal_id": "missing_audio",
                        "signal_type": "error",
                        "severity": "high",
                        "message": "No audio bytes available for analysis.",
                    }
                ],
                proxy_disclaimer=DEFAULT_PROXY_DISCLAIMER,
                metadata={"analyzer": self.name},
            )
        try:
            m, sigs, strengths, risks = analyze_bytes_to_metrics(audio_bytes, transcript_text, asr_confidence, speech_cfg)
        except Exception as e:
            return SpeechAnalysisPacket(
                analysis_id=str(uuid.uuid4()),
                session_id=session_id,
                turn_id=turn_id,
                asset_id=asset_id,
                metrics={},
                signals=[
                    {
                        "signal_id": "analysis_error",
                        "signal_type": "error",
                        "severity": "medium",
                        "message": str(e),
                    }
                ],
                proxy_disclaimer=DEFAULT_PROXY_DISCLAIMER,
                metadata={"analyzer": self.name, "error": str(e)},
            )

        ped_ids: list[str] = []
        pkt = SpeechAnalysisPacket(
            analysis_id=str(uuid.uuid4()),
            session_id=session_id,
            turn_id=turn_id,
            asset_id=asset_id,
            metrics=m.model_dump(),
            signals=[s.model_dump() for s in sigs],
            strengths=strengths,
            risks=risks,
            recommended_pedagogy_item_ids=ped_ids,
            proxy_disclaimer=DEFAULT_PROXY_DISCLAIMER,
            metadata={
                "analyzer": self.name,
                "rubric_hints": rubric_tags_for_signals([s.model_dump() for s in sigs]),
            },
        )
        return pkt

    def analyze_session(
        self,
        *,
        session_id: str,
        turn_packets: list[SpeechAnalysisPacket],
        speech_cfg: dict[str, Any],
    ) -> SessionSpeechReport:
        pdicts = [p.model_dump() for p in turn_packets]
        agg = aggregate_turn_metrics(pdicts)
        all_sigs: list[dict[str, Any]] = []
        for p in turn_packets:
            all_sigs.extend(p.signals)
        risks: list[str] = []
        strengths: list[str] = []
        for p in turn_packets:
            risks.extend(p.risks)
            strengths.extend(p.strengths)
        actions = []
        if any("pause" in str(s.get("signal_id", "")) for s in all_sigs):
            actions.append("Practice shorter phrases with fewer long silent gaps (proxy suggestion).")
        return SessionSpeechReport(
            report_id=str(uuid.uuid4()),
            session_id=session_id,
            turn_analysis_ids=[p.analysis_id for p in turn_packets],
            aggregate_metrics=agg,
            signals=all_sigs[:50],
            strengths=list(dict.fromkeys(strengths))[:12],
            risks=list(dict.fromkeys(risks))[:12],
            recommended_actions=actions[:8],
            proxy_disclaimer=DEFAULT_PROXY_DISCLAIMER,
            metadata={"analyzer": self.name, "max_turns": speech_cfg.get("max_turn_audio_analyze_count", 32)},
        )
