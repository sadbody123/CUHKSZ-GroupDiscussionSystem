"""Scoring hook for release_manifest_case (runner owns pass/fail)."""

from __future__ import annotations

from typing import Any


def score_release_manifest(details: dict[str, Any]) -> float:
    return 1.0 if details.get("manifest_keys") else 0.0
