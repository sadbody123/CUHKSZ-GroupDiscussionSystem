"""Timeline helpers."""

from __future__ import annotations

from typing import Any


def sort_progress_points(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(points, key=lambda p: str(p.get("created_at") or ""))
