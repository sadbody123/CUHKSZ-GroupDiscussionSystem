"""Merge ops settings + runtime profile speech_analysis section."""

from __future__ import annotations

from typing import Any

from app.ops.settings import UnifiedSettings, get_ops_settings
from app.runtime.profile_resolver import resolve_runtime_profile


def default_speech_section() -> dict[str, Any]:
    return {
        "enabled": False,
        "analyzer_name": "local_wave",
        "min_audio_ms": 300,
        "silence_threshold": 120.0,
        "pause_min_duration_ms": 200,
        "target_wpm_min": 80.0,
        "target_wpm_max": 200.0,
        "filler_words": ["um", "uh", "like", "you know", "actually"],
        "filler_warn_threshold": 4,
        "high_pause_ratio_threshold": 0.45,
        "low_energy_threshold": 500.0,
        "confidence_warn_threshold": 0.45,
        "max_turn_audio_analyze_count": 32,
        "coach_include_speech_section": True,
        "max_audio_ms": 600_000,
    }


def resolve_speech_config(
    *,
    profile_id: str | None,
    settings: UnifiedSettings | None = None,
) -> dict[str, Any]:
    s = settings or get_ops_settings()
    prof = resolve_runtime_profile(profile_id or s.default_runtime_profile)
    raw = dict(prof.speech_analysis) if getattr(prof, "speech_analysis", None) else {}
    base = default_speech_section()
    fillers = [x.strip() for x in (s.filler_words_csv or "").split(",") if x.strip()]
    base.update(
        {
            "enabled": bool(getattr(s, "enable_speech_analysis", True)),
            "analyzer_name": getattr(s, "default_speech_analyzer", base["analyzer_name"]),
            "pause_min_duration_ms": s.pause_min_duration_ms,
            "silence_threshold": s.pause_silence_threshold,
            "target_wpm_min": s.target_wpm_min,
            "target_wpm_max": s.target_wpm_max,
            "confidence_warn_threshold": s.confidence_proxy_warn_threshold,
            "filler_words": fillers or base["filler_words"],
        }
    )
    merged = {**base, **raw}
    if not raw.get("analyzer_name"):
        merged["analyzer_name"] = getattr(s, "default_speech_analyzer", base["analyzer_name"])
    return merged
