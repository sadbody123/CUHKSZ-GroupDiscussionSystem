"""Instantiate analyzer by name."""

from __future__ import annotations

from pathlib import Path

from app.audio.analysis.constants import ANALYZER_ADVANCED_STUB, ANALYZER_LOCAL_WAVE, ANALYZER_MOCK_DELIVERY
from app.audio.analysis.providers.advanced_stub import AdvancedStubAnalyzer
from app.audio.analysis.providers.base import BaseSpeechDeliveryAnalyzer
from app.audio.analysis.providers.local_wave_analyzer import LocalWaveAnalyzer
from app.audio.analysis.providers.mock_delivery_analyzer import MockDeliveryAnalyzer


def get_speech_analyzer(
    name: str | None,
    *,
    mock_manifest_path: Path | None = None,
) -> BaseSpeechDeliveryAnalyzer:
    n = (name or ANALYZER_LOCAL_WAVE).lower().strip()
    if n in (ANALYZER_MOCK_DELIVERY, "mock"):
        return MockDeliveryAnalyzer(manifest_path=mock_manifest_path)
    if n in (ANALYZER_ADVANCED_STUB, "advanced", "stub"):
        return AdvancedStubAnalyzer()
    return LocalWaveAnalyzer()
