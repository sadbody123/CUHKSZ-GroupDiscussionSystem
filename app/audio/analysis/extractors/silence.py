"""Silence / pause estimation from amplitude frames (deterministic)."""

from __future__ import annotations

import struct
from typing import Any


def analyze_silence_pcm(
    frames_bytes: bytes,
    *,
    sample_rate: int,
    channels: int,
    sample_width: int,
    silence_threshold_abs: float,
    pause_min_frames: int,
) -> dict[str, Any]:
    """Classify each frame as speech/silence; count pauses as consecutive silence runs >= pause_min_frames."""
    if sample_width != 2 or channels < 1:
        return {"silence_ms": 0, "pause_count": 0, "pause_ratio": 0.0, "active_speech_ms": 0}
    frame_bytes = sample_width * channels
    nframes = len(frames_bytes) // frame_bytes
    if nframes == 0:
        return {"silence_ms": 0, "pause_count": 0, "pause_ratio": 0.0, "active_speech_ms": 0}
    is_sil: list[bool] = []
    for i in range(nframes):
        off = i * frame_bytes
        chunk = frames_bytes[off : off + 2]
        if len(chunk) < 2:
            break
        v = abs(struct.unpack("<h", chunk)[0])
        is_sil.append(v < silence_threshold_abs)
    silence_frames = sum(1 for x in is_sil if x)
    speech_frames = nframes - silence_frames
    dur_ms = int(1000 * nframes / sample_rate) if sample_rate > 0 else 0
    silence_ms = int(1000 * silence_frames / sample_rate) if sample_rate > 0 else 0
    active_ms = max(0, dur_ms - silence_ms)

    pause_count = 0
    run = 0
    for sil in is_sil:
        if sil:
            run += 1
        else:
            if run >= pause_min_frames:
                pause_count += 1
            run = 0
    if run >= pause_min_frames:
        pause_count += 1

    ratio = silence_frames / nframes if nframes else 0.0
    return {
        "silence_ms": silence_ms,
        "pause_count": pause_count,
        "pause_ratio": round(ratio, 4),
        "active_speech_ms": active_ms,
    }
