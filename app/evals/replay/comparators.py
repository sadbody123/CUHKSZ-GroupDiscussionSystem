"""Simple diff helpers for replay / regression."""

from __future__ import annotations

from typing import Any


def signal_diff(old_ids: set[str], new_ids: set[str]) -> dict[str, Any]:
    return {"added": sorted(new_ids - old_ids), "removed": sorted(old_ids - new_ids)}
