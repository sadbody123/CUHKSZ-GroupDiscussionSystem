"""Skill taxonomy and shared learner constants."""

from __future__ import annotations

# Text / discussion skills (heuristic mastery dimensions)
TEXT_SKILL_IDS: tuple[str, ...] = (
    "content_support",
    "example_usage",
    "interaction",
    "discussion_language",
    "turn_concision",
    "rebuttal_clarity",
    "teammate_support",
    "topic_focus",
)

# Speech / delivery proxy skills — training heuristics only
SPEECH_PROXY_SKILL_IDS: tuple[str, ...] = (
    "fluency_proxy",
    "pause_management_proxy",
    "pace_control_proxy",
    "confidence_proxy",
    "delivery_proxy",
)

ALL_SKILL_IDS: tuple[str, ...] = TEXT_SKILL_IDS + SPEECH_PROXY_SKILL_IDS

SPEECH_PROXY_DISCLAIMER_DEFAULT: str = (
    "Speech-related scores are heuristic training proxies based on audio metrics; "
    "they are not official pronunciation or fluency grades."
)

SKILL_DISPLAY_NAMES: dict[str, str] = {
    "content_support": "Content support",
    "example_usage": "Example usage",
    "interaction": "Interaction / participation",
    "discussion_language": "Discussion language",
    "turn_concision": "Turn concision",
    "rebuttal_clarity": "Rebuttal / linkage clarity",
    "teammate_support": "Teammate support language",
    "topic_focus": "Topic focus",
    "fluency_proxy": "Fluency (proxy)",
    "pause_management_proxy": "Pause management (proxy)",
    "pace_control_proxy": "Pace control (proxy)",
    "confidence_proxy": "Delivery confidence (proxy)",
    "delivery_proxy": "Overall delivery (proxy)",
}
