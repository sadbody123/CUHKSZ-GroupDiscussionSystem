"""Core metric assembly from WAV bytes + transcript."""

from __future__ import annotations

from typing import Any

from app.audio.analysis.extractors.confidence_proxy import blend_confidence_proxy
from app.audio.analysis.extractors.energy import pcm_mono_int16_frames, rms_and_peak
from app.audio.analysis.extractors.silence import analyze_silence_pcm
from app.audio.analysis.extractors.tempo import chars_per_second, words_per_minute
from app.audio.analysis.extractors.transcript_features import count_filler, repetition_proxy, word_and_char_counts
from app.audio.analysis.extractors.wav_reader import read_wav_bytes
from app.audio.analysis.schemas.metrics import DeliveryMetrics
from app.audio.analysis.scoring.rules import evaluate_delivery_rules


def _fluency_score(pause_ratio: float | None, filler_ratio: float, wpm: float | None, wpm_min: float, wpm_max: float) -> float:
    s = 0.7
    if pause_ratio is not None:
        s -= 0.4 * min(1.0, pause_ratio)
    s -= 0.2 * min(1.0, filler_ratio * 3)
    if wpm is not None:
        if wpm < wpm_min or wpm > wpm_max:
            s -= 0.15
    return max(0.0, min(1.0, round(s, 4)))


def _delivery_score(m: DeliveryMetrics) -> float:
    parts = []
    if m.fluency_proxy_score is not None:
        parts.append(m.fluency_proxy_score)
    if m.pronunciation_proxy_score is not None:
        parts.append(m.pronunciation_proxy_score)
    if not parts:
        return 0.5
    return round(sum(parts) / len(parts), 4)


def analyze_bytes_to_metrics(
    audio_bytes: bytes,
    transcript_text: str,
    asr_confidence: float | None,
    speech_cfg: dict[str, Any],
) -> tuple[DeliveryMetrics, list, list, list]:
    silence_thr = float(speech_cfg.get("silence_threshold", 120.0))
    pause_ms = int(speech_cfg.get("pause_min_duration_ms", 200))
    wpm_min = float(speech_cfg.get("target_wpm_min", 80))
    wpm_max = float(speech_cfg.get("target_wpm_max", 200))
    fillers_list = list(speech_cfg.get("filler_words") or ["um", "uh", "like", "you know", "actually"])

    info = read_wav_bytes(audio_bytes)
    sr = info.sample_rate
    sw = info.sample_width
    ch = info.channels
    pcm = info.frames_bytes
    pause_frames = max(1, int(sr * (pause_ms / 1000.0)))

    sil = analyze_silence_pcm(
        pcm,
        sample_rate=sr,
        channels=ch,
        sample_width=sw,
        silence_threshold_abs=silence_thr,
        pause_min_frames=pause_frames,
    )
    samples = pcm_mono_int16_frames(pcm, sw, ch)
    rms, peak = rms_and_peak(samples)

    wc, cc = word_and_char_counts(transcript_text)
    fillers = count_filler(transcript_text, fillers_list)
    rep = repetition_proxy(transcript_text)

    active_ms = int(sil["active_speech_ms"])
    dur_ms = info.duration_ms
    wpm = words_per_minute(wc, active_ms, dur_ms)
    cps = chars_per_second(cc, active_ms, dur_ms)

    filler_ratio = fillers / max(1, wc)
    pause_ratio = float(sil["pause_ratio"])
    conf = blend_confidence_proxy(asr_confidence, filler_ratio=filler_ratio, pause_ratio=pause_ratio, word_count=wc)

    flu = _fluency_score(pause_ratio, filler_ratio, wpm, wpm_min, wpm_max)
    pron = conf
    m = DeliveryMetrics(
        duration_ms=dur_ms,
        active_speech_ms=active_ms,
        silence_ms=int(sil["silence_ms"]),
        pause_count=int(sil["pause_count"]),
        pause_ratio=pause_ratio,
        transcript_word_count=wc,
        transcript_char_count=cc,
        words_per_minute=wpm,
        chars_per_second=cps,
        rms_energy=round(rms, 4),
        peak_amplitude=round(peak, 4),
        filler_count=fillers,
        repetition_count=rep,
        asr_confidence=asr_confidence,
        pronunciation_proxy_score=pron,
        fluency_proxy_score=flu,
        delivery_proxy_score=None,
        metadata={"sample_rate": sr, "channels": ch},
    )
    m.delivery_proxy_score = _delivery_score(m)

    sigs, strengths, risks = evaluate_delivery_rules(m, speech_cfg=speech_cfg)
    return m, sigs, strengths, risks
