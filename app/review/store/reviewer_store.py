"""Filesystem reviewer profiles."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.review.schemas.reviewer import ReviewerProfile

_SAFE = re.compile(r"^[\w.\-]+$")


class ReviewerStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, reviewer_id: str) -> Path:
        if not _SAFE.match(reviewer_id):
            raise ValueError("invalid reviewer_id")
        return self._root / f"{reviewer_id}.json"

    def save_reviewer(self, profile: ReviewerProfile) -> Path:
        p = self._path(profile.reviewer_id)
        p.write_text(json.dumps(profile.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_reviewer(self, reviewer_id: str) -> ReviewerProfile | None:
        p = self._path(reviewer_id)
        if not p.is_file():
            return None
        return ReviewerProfile.model_validate_json(p.read_text(encoding="utf-8"))

    def list_reviewers(self) -> list[ReviewerProfile]:
        out: list[ReviewerProfile] = []
        for f in sorted(self._root.glob("*.json")):
            try:
                out.append(ReviewerProfile.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out

    def create_reviewer(self, profile: ReviewerProfile) -> ReviewerProfile:
        if self.load_reviewer(profile.reviewer_id):
            raise ValueError(f"reviewer already exists: {profile.reviewer_id}")
        self.save_reviewer(profile)
        return profile
