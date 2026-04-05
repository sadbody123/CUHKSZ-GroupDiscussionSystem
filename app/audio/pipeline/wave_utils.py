"""Generate minimal WAV bytes (stdlib only)."""

from __future__ import annotations

import hashlib
import io
import math
import wave


def wav_bytes_from_seed(seed: str, *, duration_s: float = 0.4, sample_rate: int = 8000) -> bytes:
    """Deterministic small WAV from string seed (mock TTS)."""
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)
    freq = 200 + (h % 400)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        n = int(duration_s * sample_rate)
        frames = []
        for i in range(n):
            t = i / sample_rate
            sample = int(0.2 * 32767 * math.sin(2 * math.pi * freq * t))
            frames.append(sample.to_bytes(2, byteorder="little", signed=True))
        w.writeframes(b"".join(frames))
    return buf.getvalue()
