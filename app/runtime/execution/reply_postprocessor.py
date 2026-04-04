"""Lightweight reply cleanup."""

from __future__ import annotations


def postprocess_reply(text: str, max_chars: int | None = None) -> str:
    t = text.strip()
    if max_chars is not None and len(t) > max_chars:
        return t[: max_chars] + ("…" if max_chars > 1 else "")
    return t
