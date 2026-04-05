"""Text-based fluency proxies."""

from __future__ import annotations

import re
from collections import Counter


def count_filler(text: str, fillers: list[str]) -> int:
    t = text.lower()
    n = 0
    for f in fillers:
        pat = r"\b" + re.escape(f.lower()) + r"\b"
        n += len(re.findall(pat, t))
    return n


def repetition_proxy(text: str) -> int:
    """Simple repeated word stem count (heuristic)."""
    words = re.findall(r"[A-Za-z']+", text.lower())
    if len(words) < 2:
        return 0
    c = Counter(words)
    return sum(max(0, v - 1) for v in c.values())


def word_and_char_counts(text: str) -> tuple[int, int]:
    words = re.findall(r"\S+", text.strip())
    return len(words), len(text)
