"""Publication records and published artifact pointers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.authoring.schemas.publication import PublicationRecord

_SAFE = re.compile(r"^[\w.\-]+$")


class PublicationStore:
    def __init__(self, publications_dir: Path, published_root: Path, *, project_root: Path) -> None:
        self._pub_dir = publications_dir.resolve()
        self._published_root = published_root.resolve()
        self._project_root = project_root.resolve()
        self._pub_dir.mkdir(parents=True, exist_ok=True)
        self._published_root.mkdir(parents=True, exist_ok=True)

    def _record_path(self, publication_id: str) -> Path:
        if not _SAFE.match(publication_id):
            raise ValueError("invalid publication_id")
        return self._pub_dir / f"{publication_id}.json"

    def save_publication_record(self, rec: PublicationRecord) -> Path:
        p = self._record_path(rec.publication_id)
        p.write_text(json.dumps(rec.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_publication_record(self, publication_id: str) -> PublicationRecord | None:
        p = self._record_path(publication_id)
        if not p.is_file():
            return None
        return PublicationRecord.model_validate_json(p.read_text(encoding="utf-8"))

    def list_publications(self, *, artifact_type: str | None = None) -> list[PublicationRecord]:
        out: list[PublicationRecord] = []
        for f in sorted(self._pub_dir.glob("*.json")):
            try:
                r = PublicationRecord.model_validate_json(f.read_text(encoding="utf-8"))
                if artifact_type and r.artifact_type != artifact_type:
                    continue
                out.append(r)
            except Exception:
                continue
        return out

    def resolve_latest_published_version(self, artifact_id: str, artifact_type: str) -> PublicationRecord | None:
        rows = [r for r in self.list_publications(artifact_type=artifact_type) if r.artifact_id == artifact_id]
        if not rows:
            return None
        return max(rows, key=lambda x: (x.published_at, x.published_version))

    def load_published_artifact_payload(self, rec: PublicationRecord) -> dict[str, Any] | None:
        """Load JSON payload from output_ref (project-relative, under published_root, or absolute)."""
        ref = rec.output_ref
        path = Path(ref)
        if not path.is_absolute():
            cand = (self._published_root / ref).resolve()
            if cand.is_file():
                path = cand
            else:
                path = (self._project_root / ref).resolve()
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
