"""Named rule-detected signals."""

from __future__ import annotations

EXAMPLE_CUES = (
    "for example",
    "for instance",
    "such as",
    "e.g.",
    "eg.",
)

DISCUSSION_LANG_CUES = (
    "i agree",
    "i see your point",
    "in response to",
    "i want to clarify",
    "what do you mean by",
)

SUPPORT_TEAM_CUES = (
    "i want to support my teammate",
    "exactly, and",
)

LINKAGE_CUES = (
    "in response to",
    "as for your point",
    "speaking of what you said",
)


def contains_any(text: str, cues: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(c in low for c in cues)
