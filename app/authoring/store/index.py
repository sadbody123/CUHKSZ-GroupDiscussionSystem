"""Lightweight authoring index (rebuilt from stores)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.authoring.store.draft_store import DraftStore
from app.authoring.store.patch_store import PatchStore
from app.authoring.store.publication_store import PublicationStore


def rebuild_authoring_index(
    *,
    index_path: Path,
    drafts: DraftStore,
    patches: PatchStore,
    publications: PublicationStore,
) -> dict[str, Any]:
    drows = drafts.list_drafts()
    prows = patches.list_patches()
    pubrows = publications.list_publications()
    data: dict[str, Any] = {
        "draft_ids": [d.draft_id for d in drows],
        "drafts_by_status": {},
        "patch_ids": [p.patch_id for p in prows],
        "publication_ids": [p.publication_id for p in pubrows],
        "artifact_index": {},
    }
    for d in drows:
        data["drafts_by_status"].setdefault(d.status, []).append(d.draft_id)
        key = f"{d.artifact_type}:{d.artifact_id}"
        data["artifact_index"].setdefault(key, []).append({"kind": "draft", "id": d.draft_id})
    for p in pubrows:
        key = f"{p.artifact_type}:{p.artifact_id}"
        data["artifact_index"].setdefault(key, []).append({"kind": "publication", "id": p.publication_id})
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def load_authoring_index(index_path: Path) -> dict[str, Any] | None:
    if not index_path.is_file():
        return None
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
