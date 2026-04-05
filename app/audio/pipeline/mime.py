"""MIME helpers."""

from __future__ import annotations

_ALLOWED = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "application/octet-stream",
}


def normalize_audio_mime(m: str | None) -> str:
    if not m:
        return "audio/wav"
    m = m.split(";")[0].strip().lower()
    return m if m in _ALLOWED else "application/octet-stream"
