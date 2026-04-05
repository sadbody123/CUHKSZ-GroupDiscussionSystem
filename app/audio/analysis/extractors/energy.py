"""Simple RMS / peak from 16-bit PCM mono frames."""

from __future__ import annotations

import math
import struct


def pcm_mono_int16_frames(frames_bytes: bytes, sample_width: int, channels: int) -> list[int]:
    if sample_width != 2:
        return []
    n = len(frames_bytes) // (sample_width * channels)
    out: list[int] = []
    step = sample_width * channels
    for i in range(n):
        chunk = frames_bytes[i * step : i * step + 2]
        if len(chunk) < 2:
            break
        v = struct.unpack("<h", chunk)[0]
        out.append(v)
    return out


def rms_and_peak(samples: list[int]) -> tuple[float, float]:
    if not samples:
        return 0.0, 0.0
    acc = sum(s * s for s in samples)
    rms = math.sqrt(acc / len(samples))
    peak = float(max(abs(s) for s in samples))
    return rms, peak
