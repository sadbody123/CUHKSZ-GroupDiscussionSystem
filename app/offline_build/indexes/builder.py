"""Build snapshot-local indexes under ``indexes/``."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.indexing.constants import INDEX_SCHEMA_VERSION, MODE_LEXICAL, MODE_VECTOR
from app.indexing.embedders import get_embedder
from app.indexing.lexical.builder import write_lexical_index
from app.indexing.schemas.index_manifest import IndexManifest
from app.indexing.vector.builder import build_vectors_for_docs
from app.runtime.snapshot_loader import load_snapshot


def _doc_evidence(ev: Any) -> dict[str, Any]:
    return {
        "item_id": ev.evidence_id,
        "text": ev.text,
        "title": ev.title,
        "tags": list(ev.topic_tags or []),
        "source_type": ev.source_type,
        "metadata": {
            "stance_hint": ev.stance_hint,
            "quality_score": ev.quality_score,
            "credibility_score": ev.credibility_score,
        },
    }


def _doc_pedagogy(p: Any) -> dict[str, Any]:
    return {
        "item_id": p.item_id,
        "text": p.content,
        "title": p.category or p.item_type,
        "tags": list(p.tags or []),
        "source_type": "pedagogy",
        "metadata": {"item_type": p.item_type},
    }


def _doc_topic(c: Any) -> dict[str, Any]:
    blob = " ".join(
        [
            c.topic or "",
            c.summary or "",
            " ".join(c.example_hints or []),
        ]
    )
    return {
        "item_id": c.topic_id,
        "text": blob,
        "title": c.topic,
        "tags": list(c.tags or []),
        "source_type": "topic_card",
        "metadata": {},
    }


def build_snapshot_indexes(
    snapshot_dir: Path,
    *,
    stores: list[str],
    modes: list[str],
    embedder: str = "hash",
    dimension: int = 128,
) -> IndexManifest:
    snap = snapshot_dir.resolve()
    bundle = load_snapshot(snap)
    idx_root = snap / "indexes"
    idx_root.mkdir(parents=True, exist_ok=True)

    mode_set = {m.lower() for m in modes}
    want_lex = MODE_LEXICAL in mode_set
    want_vec = MODE_VECTOR in mode_set

    embedder_impl = get_embedder(embedder, dimension=dimension)
    counts: dict[str, int] = {}
    files: list[dict[str, Any]] = []
    store_dirs: dict[str, Path] = {}

    for store in stores:
        sdir = idx_root / store
        sdir.mkdir(parents=True, exist_ok=True)
        store_dirs[store] = sdir
        docs: list[dict[str, Any]] = []
        if store == "evidence":
            docs = [_doc_evidence(x) for x in bundle.evidence_index]
        elif store == "pedagogy":
            docs = [_doc_pedagogy(x) for x in bundle.pedagogy_items]
        elif store == "topics":
            docs = [_doc_topic(x) for x in bundle.topic_cards]
        else:
            continue
        counts[store] = len(docs)
        items_path = sdir / "items.jsonl"
        with items_path.open("w", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        files.append({"store": store, "path": str(items_path.relative_to(snap)), "kind": "items_jsonl"})

        lex_path = sdir / "lexical_index.json"
        if want_lex:
            write_lexical_index(lex_path, docs)
            files.append({"store": store, "path": str(lex_path.relative_to(snap)), "kind": "lexical_index"})

        if want_vec and docs:
            npy = sdir / "vector_embeddings.npy"
            meta = sdir / "vector_meta.json"
            n, dim = build_vectors_for_docs(embedder_impl, docs, npy_path=npy, meta_path=meta)
            files.append({"store": store, "path": str(npy.relative_to(snap)), "kind": "vector_npy"})
            files.append({"store": store, "path": str(meta.relative_to(snap)), "kind": "vector_meta"})

    avail_modes: list[str] = []
    if want_lex:
        avail_modes.append(MODE_LEXICAL)
    if want_vec:
        avail_modes.append(MODE_VECTOR)
    if want_lex and want_vec:
        avail_modes.append("hybrid")

    manifest = IndexManifest(
        index_id=str(uuid4()),
        snapshot_id=bundle.manifest.snapshot_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        schema_version=INDEX_SCHEMA_VERSION,
        embedder_name=embedder_impl.name,
        embedder_model=getattr(embedder_impl, "model_name", None),
        dimension=getattr(embedder_impl, "dimension", None) if hasattr(embedder_impl, "dimension") else dimension,
        stores=list(stores),
        available_modes=avail_modes,
        item_counts=counts,
        files=files,
        metadata={"modes_requested": list(modes)},
    )
    (idx_root / "manifest.json").write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return manifest
