"""Speaking rate proxies from duration and transcript."""

from __future__ import annotations


def words_per_minute(word_count: int, active_speech_ms: int | None, duration_ms: int | None) -> float | None:
    base_ms = active_speech_ms if active_speech_ms and active_speech_ms > 0 else duration_ms
    if not base_ms or base_ms <= 0 or word_count < 0:
        return None
    minutes = base_ms / 60000.0
    if minutes <= 0:
        return None
    return round(word_count / minutes, 2)


def chars_per_second(char_count: int, active_speech_ms: int | None, duration_ms: int | None) -> float | None:
    base_ms = active_speech_ms if active_speech_ms and active_speech_ms > 0 else duration_ms
    if not base_ms or base_ms <= 0 or char_count < 0:
        return None
    sec = base_ms / 1000.0
    if sec <= 0:
        return None
    return round(char_count / sec, 3)
