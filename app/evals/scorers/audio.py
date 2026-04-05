"""Optional helpers for audio eval assertions (phase 9)."""

from __future__ import annotations

from typing import Any


def count_assets_matching(assets: list[Any], *, mime_type: str | None = None) -> int:
    n = 0
    for a in assets:
        if mime_type is None:
            n += 1
            continue
        mt = getattr(a, "mime_type", None) if not isinstance(a, dict) else a.get("mime_type")
        if mt == mime_type:
            n += 1
    return n
