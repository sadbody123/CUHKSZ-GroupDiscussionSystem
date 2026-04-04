"""Conservative text cleaning for reproducible offline build."""

from __future__ import annotations

import re

_BOILERPLATE = re.compile(
    r"(?i)\b(lorem ipsum|待补充|todo:|tbd\b|placeholder|暂无内容|无正文)\b"
)
_MULTISPACE = re.compile(r"[ \t]+")
_MULTIBLANK = re.compile(r"\n{3,}")


def clean_text(raw: str) -> str:
    if not raw:
        return ""
    s = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    s = _BOILERPLATE.sub(" ", s)
    s = _MULTISPACE.sub(" ", s)
    s = _MULTIBLANK.sub("\n\n", s)
    return s.strip()


def is_low_value_text(text: str, min_chars: int = 20) -> bool:
    return len(text.strip()) < min_chars
