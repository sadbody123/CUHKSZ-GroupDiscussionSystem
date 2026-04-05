"""Lightweight learner -> assignment index (backed by assignment store index.json)."""

from __future__ import annotations

import json
from pathlib import Path


def learner_assignment_ids(root: Path, learner_id: str) -> list[str]:
    idx = root / "index.json"
    if not idx.is_file():
        return []
    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
        return list(data.get("learner_map", {}).get(learner_id, []))
    except (OSError, json.JSONDecodeError, TypeError):
        return []
