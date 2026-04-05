"""Phase 10 speech proxy analysis smoke tests."""

from __future__ import annotations

from app.audio.analysis.pipeline.analyze_asset import analyze_bytes_to_metrics
from app.audio.analysis.config import resolve_speech_config


def test_analyze_bytes_stable_metrics() -> None:
    from app.audio.pipeline.wave_utils import wav_bytes_from_seed

    b = wav_bytes_from_seed("fixture-a", duration_s=0.5, sample_rate=8000)
    cfg = resolve_speech_config(profile_id="speech_default")
    m, _sigs, _st, _rk = analyze_bytes_to_metrics(b, "hello world test", 0.9, cfg)
    assert m.duration_ms is not None
    assert m.words_per_minute is not None


def test_local_wave_analyzer_packet():
    from app.audio.analysis.providers.local_wave_analyzer import LocalWaveAnalyzer
    from app.audio.pipeline.wave_utils import wav_bytes_from_seed

    an = LocalWaveAnalyzer()
    b = wav_bytes_from_seed("x", duration_s=0.4)
    cfg = resolve_speech_config(profile_id="speech_default")
    p = an.analyze_turn(
        session_id="s",
        turn_id="t",
        asset_id="a",
        audio_bytes=b,
        transcript_text="one two three four",
        asr_confidence=0.8,
        speech_cfg=cfg,
    )
    assert p.proxy_disclaimer
    assert p.metrics
