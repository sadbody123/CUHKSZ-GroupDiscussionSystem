"""Helpers for speech_delivery eval (optional)."""

from __future__ import annotations

from typing import Any


def has_disclaimer(report: dict[str, Any]) -> bool:
    return bool(report.get("proxy_disclaimer"))
