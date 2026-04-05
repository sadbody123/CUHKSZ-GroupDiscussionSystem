"""Intro / summary ordering per team."""

from __future__ import annotations

from typing import Any


def intro_order(participants: list[dict[str, Any]]) -> list[str]:
    ps = sorted(
        [p for p in participants if p.get("controller_type") != "system"],
        key=lambda x: int(x.get("intro_priority") or 99),
    )
    return [str(p["participant_id"]) for p in ps]


def summary_order(participants: list[dict[str, Any]]) -> list[str]:
    ps = sorted(
        [p for p in participants if p.get("controller_type") != "system"],
        key=lambda x: int(x.get("summary_priority") or 99),
    )
    return [str(p["participant_id"]) for p in ps]
