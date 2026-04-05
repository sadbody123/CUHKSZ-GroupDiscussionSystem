"""Read WAV metadata and PCM frames (stdlib wave only)."""

from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WavInfo:
    sample_rate: int
    channels: int
    sample_width: int
    frame_count: int
    duration_ms: int
    frames_bytes: bytes


def read_wav(path: Path) -> WavInfo:
    p = path.resolve()
    with wave.open(str(p), "rb") as w:
        ch = w.getnchannels()
        sw = w.getsampwidth()
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    dur_ms = int(1000 * n / sr) if sr > 0 else 0
    return WavInfo(
        sample_rate=sr,
        channels=ch,
        sample_width=sw,
        frame_count=n,
        duration_ms=dur_ms,
        frames_bytes=raw,
    )


def read_wav_bytes(data: bytes) -> WavInfo:
    import io

    with wave.open(io.BytesIO(data), "rb") as w:
        ch = w.getnchannels()
        sw = w.getsampwidth()
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    dur_ms = int(1000 * n / sr) if sr > 0 else 0
    return WavInfo(
        sample_rate=sr,
        channels=ch,
        sample_width=sw,
        frame_count=n,
        duration_ms=dur_ms,
        frames_bytes=raw,
    )
