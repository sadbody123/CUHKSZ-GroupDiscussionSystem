"""Simple tokenizer for lexical scoring."""

from __future__ import annotations

import re

_TOKEN = re.compile(r"[a-z0-9]+", re.I)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "")]
