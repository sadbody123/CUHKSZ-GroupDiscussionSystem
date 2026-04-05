"""Learner index for fast listing (CLI / API)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.learner.schemas.learner import LearnerProfile


def rebuild_learner_index(root: Path) -> Path:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        pf = d / "profile.json"
        if not pf.is_file():
            continue
        try:
            p = LearnerProfile.model_validate_json(pf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rows.append(
            {
                "learner_id": p.learner_id,
                "display_name": p.display_name,
                "total_sessions": p.total_sessions,
                "updated_at": p.updated_at,
            }
        )
    idx = root / "index.json"
    tmp = idx.with_suffix(".tmp")
    tmp.write_text(json.dumps({"learners": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(idx)
    return idx


class LearnerIndex:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def summaries(self) -> list[dict[str, Any]]:
        p = self._root / "index.json"
        if not p.is_file():
            rebuild_learner_index(self._root)
            p = self._root / "index.json"
        if not p.is_file():
            return []
        raw = json.loads(p.read_text(encoding="utf-8"))
        return list(raw.get("learners") or [])
