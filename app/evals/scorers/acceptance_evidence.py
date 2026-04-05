"""Scoring hook for acceptance_evidence_case."""

from __future__ import annotations

from typing import Any


def score_acceptance_evidence(details: dict[str, Any]) -> float:
    return 1.0 if "passed_checks" in details and "failed_checks" in details else 0.0
