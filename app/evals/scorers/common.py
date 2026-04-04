"""Shared scoring utilities."""

from __future__ import annotations


def bool_score(passed: bool) -> float:
    return 1.0 if passed else 0.0
