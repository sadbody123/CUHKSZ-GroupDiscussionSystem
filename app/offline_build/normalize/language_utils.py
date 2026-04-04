"""Lightweight language hints (no external models)."""

from __future__ import annotations

import re

_CJK = re.compile(r"[\u4e00-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")


def guess_language_hint(text: str) -> str | None:
    if not text:
        return None
    sample = text[:2000]
    cjk = len(_CJK.findall(sample))
    lat = len(_LATIN.findall(sample))
    if cjk > lat * 2:
        return "zh"
    if lat > cjk * 2:
        return "en"
    return "mixed"
