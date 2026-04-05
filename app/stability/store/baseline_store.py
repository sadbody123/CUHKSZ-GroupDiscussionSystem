"""Golden / baseline JSON helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def required_keys_present(obj: dict[str, Any], keys: list[str]) -> bool:
    return all(k in obj for k in keys)
