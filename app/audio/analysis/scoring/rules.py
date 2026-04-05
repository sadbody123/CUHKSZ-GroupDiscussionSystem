"""Rule-based signals from metrics + speech_analysis profile section."""

from __future__ import annotations

from typing import Any

from app.audio.analysis.schemas.metrics import DeliveryMetrics
from app.audio.analysis.schemas.signals import DeliverySignal


def _cfg(speech: dict[str, Any], key: str, default: Any) -> Any:
    return speech.get(key, default)


def evaluate_delivery_rules(
    m: DeliveryMetrics,
    *,
    speech_cfg: dict[str, Any],
) -> tuple[list[DeliverySignal], list[str], list[str]]:
    """Return signals, strengths, risks (human-readable)."""
    signals: list[DeliverySignal] = []
    strengths: list[str] = []
    risks: list[str] = []

    high_pause = float(_cfg(speech_cfg, "high_pause_ratio_threshold", 0.45))
    filler_thr = int(_cfg(speech_cfg, "filler_warn_threshold", 4))
    wpm_min = float(_cfg(speech_cfg, "target_wpm_min", 80))
    wpm_max = float(_cfg(speech_cfg, "target_wpm_max", 200))
    low_e = float(_cfg(speech_cfg, "low_energy_threshold", 500.0))
    min_ms = int(_cfg(speech_cfg, "min_audio_ms", 500))
    max_ms = int(_cfg(speech_cfg, "max_audio_ms", 300000))
    conf_warn = float(_cfg(speech_cfg, "confidence_warn_threshold", 0.45))

    pr = m.pause_ratio
    if pr is not None and pr > high_pause:
        signals.append(
            DeliverySignal(
                signal_id="speech_pause_density",
                signal_type="risk",
                severity="medium",
                message="High silence / pause ratio (proxy): consider smoother pacing.",
                metric_name="pause_ratio",
                evidence={"pause_ratio": pr, "threshold": high_pause},
            )
        )
        risks.append("Fluency (proxy): frequent pauses detected.")

    fc = m.filler_count
    if fc is not None and fc >= filler_thr:
        signals.append(
            DeliverySignal(
                signal_id="speech_filler_words",
                signal_type="risk",
                severity="low",
                message="Elevated filler word count in transcript (proxy).",
                metric_name="filler_count",
                evidence={"filler_count": fc, "threshold": filler_thr},
            )
        )
        risks.append("Delivery (proxy): filler words.")

    wpm = m.words_per_minute
    if wpm is not None:
        if wpm < wpm_min:
            signals.append(
                DeliverySignal(
                    signal_id="speech_slow_rate",
                    signal_type="risk",
                    severity="medium",
                    message="Speaking rate appears slow vs target band (proxy).",
                    metric_name="words_per_minute",
                    evidence={"wpm": wpm, "min": wpm_min, "max": wpm_max},
                )
            )
            risks.append("Pace (proxy): slow WPM.")
        elif wpm > wpm_max:
            signals.append(
                DeliverySignal(
                    signal_id="speech_fast_rate",
                    signal_type="risk",
                    severity="medium",
                    message="Speaking rate appears fast vs target band (proxy).",
                    metric_name="words_per_minute",
                    evidence={"wpm": wpm, "min": wpm_min, "max": wpm_max},
                )
            )
            risks.append("Pace (proxy): fast WPM.")

    dur = m.duration_ms
    wc = m.transcript_word_count or 0
    if dur is not None and dur < min_ms:
        signals.append(
            DeliverySignal(
                signal_id="speech_too_short",
                signal_type="risk",
                severity="low",
                message="Audio clip is very short (proxy).",
                metric_name="duration_ms",
                evidence={"duration_ms": dur, "min_ms": min_ms},
            )
        )
    if dur is not None and dur > max_ms:
        signals.append(
            DeliverySignal(
                signal_id="speech_too_long",
                signal_type="info",
                severity="low",
                message="Audio duration is long; consider segmenting practice (proxy).",
                metric_name="duration_ms",
                evidence={"duration_ms": dur, "max_ms": max_ms},
            )
        )

    rms = m.rms_energy
    if rms is not None and rms < low_e and rms > 0:
        signals.append(
            DeliverySignal(
                signal_id="speech_low_volume_proxy",
                signal_type="risk",
                severity="low",
                message="Low RMS energy vs threshold (volume proxy, not dBSPL).",
                metric_name="rms_energy",
                evidence={"rms": rms, "threshold": low_e},
            )
        )
        risks.append("Volume (proxy): low energy.")

    conf = m.pronunciation_proxy_score
    if conf is not None and conf < conf_warn:
        signals.append(
            DeliverySignal(
                signal_id="speech_confidence_proxy_low",
                signal_type="risk",
                severity="medium",
                message="Low clarity / confidence proxy (not pronunciation score).",
                metric_name="pronunciation_proxy_score",
                evidence={"score": conf, "threshold": conf_warn},
            )
        )
        risks.append("Pronunciation clarity (proxy only): low confidence proxy.")

    # Positive fluency band
    if (
        pr is not None
        and pr <= high_pause * 0.7
        and (fc or 0) < max(1, filler_thr // 2)
        and wpm is not None
        and wpm_min <= wpm <= wpm_max
    ):
        strengths.append("Fluency (proxy): pace and pauses within a reasonable band.")
    if (fc or 0) == 0 and wc > 3:
        strengths.append("Delivery (proxy): few filler words detected.")

    return signals, strengths, risks
