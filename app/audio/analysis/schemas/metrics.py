"""Delivery proxy metrics (heuristic, not acoustic ground truth)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DeliveryMetrics(BaseModel):
    duration_ms: int | None = None
    active_speech_ms: int | None = None
    silence_ms: int | None = None
    pause_count: int | None = None
    pause_ratio: float | None = None
    transcript_word_count: int | None = None
    transcript_char_count: int | None = None
    words_per_minute: float | None = None
    chars_per_second: float | None = None
    rms_energy: float | None = None
    peak_amplitude: float | None = None
    filler_count: int | None = None
    repetition_count: int | None = None
    asr_confidence: float | None = None
    pronunciation_proxy_score: float | None = None
    fluency_proxy_score: float | None = None
    delivery_proxy_score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
