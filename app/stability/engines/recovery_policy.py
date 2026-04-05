"""Deterministic recovery / degradation policies (documentation + lookup)."""

from __future__ import annotations

POLICIES: list[dict[str, str]] = [
    {
        "id": "missing_index",
        "trigger": "retrieval index missing or empty",
        "behavior": "fallback to lexical / rule-based retrieval where configured",
        "severity_if_unhandled": "warning",
    },
    {
        "id": "missing_audio_asset",
        "trigger": "audio asset id not on disk",
        "behavior": "degrade to text-only turn handling",
        "severity_if_unhandled": "warning",
    },
    {
        "id": "missing_speech_report",
        "trigger": "speech analysis disabled or no audio",
        "behavior": "coach feedback remains text-only",
        "severity_if_unhandled": "info",
    },
    {
        "id": "missing_learner_attachment",
        "trigger": "session without learner_id",
        "behavior": "anonymous session; analytics not tied to learner record",
        "severity_if_unhandled": "info",
    },
    {
        "id": "missing_assignment_link",
        "trigger": "assignment step not linked",
        "behavior": "treat as plain practice session",
        "severity_if_unhandled": "info",
    },
    {
        "id": "missing_review_pack",
        "trigger": "review workspace gated or pack not created",
        "behavior": "raw AI coach feedback path only",
        "severity_if_unhandled": "warning",
    },
    {
        "id": "gated_capability",
        "trigger": "capability disabled in active release profile",
        "behavior": "hide UI entry or return explanatory API message; skip E2E with note",
        "severity_if_unhandled": "error",
    },
    {
        "id": "missing_custom_publication",
        "trigger": "custom artifact not found",
        "behavior": "fallback to builtin pack/profile when explicitly allowed",
        "severity_if_unhandled": "warning",
    },
]


def recovery_policy_summary() -> dict[str, object]:
    return {"policies": list(POLICIES), "count": len(POLICIES)}


def classify_recovery_note(trigger_key: str) -> str | None:
    for p in POLICIES:
        if p["id"] == trigger_key:
            return p["behavior"]
    return None
