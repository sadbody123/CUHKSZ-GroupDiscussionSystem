"""Filesystem learner store under storage/learners/<id>/."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.learner.schemas.learner import LearnerProfile
from app.learner.schemas.plan import LearningPlan
from app.learner.schemas.progress import ProgressPoint

from .index import rebuild_learner_index


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if hasattr(data, "model_dump"):
        payload = data.model_dump()
    else:
        payload = data
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


class LearnerFileStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def learner_dir(self, learner_id: str) -> Path:
        return self._root / learner_id

    def create_learner(self, learner_id: str, display_name: str | None = None) -> LearnerProfile:
        self._root.mkdir(parents=True, exist_ok=True)
        d = self.learner_dir(learner_id)
        if d.is_dir() and (d / "profile.json").is_file():
            raise ValueError(f"learner already exists: {learner_id}")
        now = _utc_now()
        prof = LearnerProfile(
            learner_id=learner_id,
            display_name=display_name,
            created_at=now,
            updated_at=now,
            metadata={"source": "create_learner"},
        )
        d.mkdir(parents=True, exist_ok=True)
        (d / "reports").mkdir(exist_ok=True)
        (d / "plans").mkdir(exist_ok=True)
        _atomic_write_json(d / "profile.json", prof)
        _atomic_write_json(d / "timeline.json", {"points": []})
        rebuild_learner_index(self._root)
        return prof

    def load_learner_profile(self, learner_id: str) -> LearnerProfile | None:
        p = self.learner_dir(learner_id) / "profile.json"
        if not p.is_file():
            return None
        return LearnerProfile.model_validate_json(p.read_text(encoding="utf-8"))

    def save_learner_profile(self, profile: LearnerProfile) -> None:
        profile.updated_at = _utc_now()
        _atomic_write_json(self.learner_dir(profile.learner_id) / "profile.json", profile)
        rebuild_learner_index(self._root)

    def load_timeline(self, learner_id: str) -> list[dict[str, Any]]:
        p = self.learner_dir(learner_id) / "timeline.json"
        if not p.is_file():
            return []
        raw = json.loads(p.read_text(encoding="utf-8"))
        return list(raw.get("points") or [])

    def save_timeline(self, learner_id: str, points: list[ProgressPoint | dict[str, Any]]) -> None:
        serial = []
        for x in points:
            serial.append(x.model_dump() if hasattr(x, "model_dump") else dict(x))
        _atomic_write_json(self.learner_dir(learner_id) / "timeline.json", {"points": serial})
        rebuild_learner_index(self._root)

    def save_report(self, learner_id: str, report_dict: dict[str, Any]) -> Path:
        rid = str(report_dict.get("report_id") or uuid.uuid4())
        out = self.learner_dir(learner_id) / "reports" / f"{rid}.json"
        _atomic_write_json(out, report_dict)
        rebuild_learner_index(self._root)
        return out

    def save_plan(self, learner_id: str, plan: LearningPlan) -> Path:
        out = self.learner_dir(learner_id) / "plans" / f"{plan.plan_id}.json"
        _atomic_write_json(out, plan)
        rebuild_learner_index(self._root)
        return out

    def list_learners(self) -> list[str]:
        if not self._root.is_dir():
            return []
        return sorted(
            d.name for d in self._root.iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "profile.json").is_file()
        )
