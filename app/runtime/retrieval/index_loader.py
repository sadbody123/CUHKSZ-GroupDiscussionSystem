"""Load on-disk indexes next to a snapshot."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.indexing.lexical.searcher import LexicalSearcher
from app.indexing.schemas.index_manifest import IndexManifest
from app.indexing.vector.searcher import VectorSearcher


def _read_jsonl_items(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            iid = str(raw.get("item_id") or "")
            if iid:
                out[iid] = raw
    return out


@dataclass
class StoreIndexes:
    name: str
    docs_by_id: dict[str, dict[str, Any]]
    lexical: LexicalSearcher | None
    vector: VectorSearcher | None


@dataclass
class SnapshotIndexes:
    manifest: IndexManifest
    snapshot_dir: Path
    stores: dict[str, StoreIndexes]


def try_load_indexes(snapshot_dir: Path) -> SnapshotIndexes | None:
    root = snapshot_dir.resolve()
    mf_path = root / "indexes" / "manifest.json"
    if not mf_path.is_file():
        return None
    manifest = IndexManifest.model_validate(json.loads(mf_path.read_text(encoding="utf-8")))
    stores: dict[str, StoreIndexes] = {}
    for name in manifest.stores:
        sdir = root / "indexes" / name
        items_path = sdir / "items.jsonl"
        docs = _read_jsonl_items(items_path)
        lex_path = sdir / "lexical_index.json"
        lexical = LexicalSearcher(lex_path) if lex_path.is_file() else None
        npy = sdir / "vector_embeddings.npy"
        meta = sdir / "vector_meta.json"
        vector = VectorSearcher(npy, meta, docs) if npy.is_file() and meta.is_file() else None
        stores[name] = StoreIndexes(name=name, docs_by_id=docs, lexical=lexical, vector=vector)
    return SnapshotIndexes(manifest=manifest, snapshot_dir=root, stores=stores)


def has_indexes(snapshot_dir: Path) -> bool:
    return (snapshot_dir.resolve() / "indexes" / "manifest.json").is_file()
