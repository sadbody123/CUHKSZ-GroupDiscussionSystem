"""Load static markdown prompt templates for each role."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.runtime.enums import RoleType

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def prompt_template_id_for_role(role: str) -> str:
    r = role.lower().strip()
    if r == RoleType.MODERATOR.value:
        return "moderator.md"
    if r == RoleType.ALLY.value:
        return "ally.md"
    if r == RoleType.OPPONENT.value:
        return "opponent.md"
    if r == RoleType.COACH.value:
        return "coach.md"
    if r == RoleType.USER.value:
        return "user_support.md"
    return "user_support.md"


@lru_cache(maxsize=16)
def load_prompt_text(template_id: str) -> str:
    path = _PROMPTS_DIR / template_id
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")
