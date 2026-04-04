"""Normalize metadata dict values (strings, dates) without heavy NLP."""

from __future__ import annotations

from typing import Any


def normalize_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if isinstance(v, str):
            out[k] = v.strip()
        else:
            out[k] = v
    return out
