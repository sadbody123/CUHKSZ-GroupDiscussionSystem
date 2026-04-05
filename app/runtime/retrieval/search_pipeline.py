"""Indexed search used by RoleRouter."""

from __future__ import annotations

from typing import Any

from app.indexing.config import retrieval_section
from app.indexing.constants import MODE_HYBRID, MODE_LEXICAL, MODE_VECTOR
from app.indexing.embedders import get_embedder
from app.indexing.embedders.base import BaseEmbedder
from app.indexing.hybrid.merger import merge_hybrid
from app.indexing.hybrid.reranker import boost_evidence_score
from app.indexing.schemas.retrieval import RetrievalHit
from app.runtime.retrieval.index_loader import SnapshotIndexes, StoreIndexes


def _hits_from_tuples(
    tuples: list[tuple[str, float, dict[str, Any]]],
    *,
    store: str,
    mode: str,
    source_type_key: str = "source_type",
) -> list[RetrievalHit]:
    out: list[RetrievalHit] = []
    for pid, sc, meta in tuples:
        text = str(meta.get("text") or "")
        title = meta.get("title")
        st = meta.get(source_type_key)
        out.append(
            RetrievalHit(
                item_id=pid,
                store=store,
                score=float(sc),
                mode=mode,
                text=text[:2000],
                title=str(title) if title else None,
                source_type=str(st) if st else None,
                metadata=dict(meta.get("metadata") or {}),
            )
        )
    return out


def search_store(
    store: StoreIndexes,
    embedder: BaseEmbedder,
    query: str,
    *,
    mode: str,
    retrieval: dict[str, Any],
    query_tags: list[str] | None,
    store_name: str,
) -> list[RetrievalHit]:
    rc = retrieval_section(retrieval)
    m = mode.lower().strip()
    lex_k = int(rc["lexical_top_k"])
    vec_k = int(rc["vector_top_k"])
    final_k = int(rc["final_top_k"])
    title_boost = float(rc["title_boost"])
    tag_boost = float(rc["topic_tag_boost"])
    q_boost = float(rc["quality_boost"])
    c_boost = float(rc["credibility_boost"])

    if m == MODE_LEXICAL:
        if not store.lexical:
            return []
        raw = store.lexical.search(
            query,
            top_k=lex_k,
            query_tags=query_tags,
            title_boost=title_boost,
            topic_tag_boost=tag_boost,
        )
        tuples = []
        for pid, sc, d in raw:
            if store_name == "evidence":
                sc = boost_evidence_score(sc, d.get("metadata") or {}, quality_boost=q_boost, credibility_boost=c_boost)
            tuples.append((pid, sc, d))
        tuples.sort(key=lambda x: x[1], reverse=True)
        return _hits_from_tuples(tuples[:final_k], store=store_name, mode=MODE_LEXICAL)

    if m == MODE_VECTOR:
        if not store.vector:
            return []
        raw = store.vector.search(embedder, query, top_k=vec_k)
        tuples = []
        for pid, sc, d in raw:
            if store_name == "evidence":
                sc = boost_evidence_score(sc, d.get("metadata") or {}, quality_boost=q_boost, credibility_boost=c_boost)
            tuples.append((pid, sc, d))
        return _hits_from_tuples(tuples[:final_k], store=store_name, mode=MODE_VECTOR)

    if m == MODE_HYBRID:
        lex_raw: list[tuple[str, float, dict[str, Any]]] = []
        if store.lexical:
            lex_raw = store.lexical.search(
                query,
                top_k=lex_k,
                query_tags=query_tags,
                title_boost=title_boost,
                topic_tag_boost=tag_boost,
            )
        vec_raw: list[tuple[str, float, dict[str, Any]]] = []
        if store.vector:
            vec_raw = store.vector.search(embedder, query, top_k=vec_k)
        fused = merge_hybrid(
            lex_raw,
            vec_raw,
            lexical_weight=float(rc["lexical_weight"]),
            vector_weight=float(rc["vector_weight"]),
            top_k=final_k,
        )
        tuples = []
        for pid, sc, d in fused:
            full = store.docs_by_id.get(pid, d)
            if store_name == "evidence":
                sc = boost_evidence_score(sc, full.get("metadata") or {}, quality_boost=q_boost, credibility_boost=c_boost)
            tuples.append((pid, sc, full))
        tuples.sort(key=lambda x: x[1], reverse=True)
        return _hits_from_tuples(tuples[:final_k], store=store_name, mode=MODE_HYBRID)

    return []


def resolve_query_embedder(manifest_embedder: str, dimension: int | None) -> BaseEmbedder:
    dim = int(dimension or 128)
    return get_embedder(manifest_embedder or "hash", dimension=dim)
