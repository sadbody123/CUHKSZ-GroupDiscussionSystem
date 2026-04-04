"""Shared string enums for runtime orchestration."""

from __future__ import annotations

from enum import StrEnum


class RoleType(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ALLY = "ally"
    OPPONENT = "opponent"
    COACH = "coach"


class SessionPhase(StrEnum):
    PREPARE = "prepare"
    INTRO = "intro"
    DISCUSSION = "discussion"
    SUMMARY = "summary"
    FEEDBACK = "feedback"
    ENDED = "ended"
