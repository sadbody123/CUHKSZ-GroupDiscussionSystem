"""Build EvidenceIndexItem rows from chunks + normalized documents."""

from __future__ import annotations

from app.offline_build.evidence_index.citation import build_citation
from app.offline_build.evidence_index.scoring import (
    credibility_score,
    infer_stance_hint,
    quality_score,
)
from app.offline_build.classify.evidence_type import infer_evidence_type
from app.offline_build.classify.source_type import default_source_type_for_table
from app.offline_build.classify.topic_tags import infer_topic_tags
from app.schemas.evidence import EvidenceChunk
from app.schemas.evidence_index import EvidenceIndexItem
from app.schemas.normalized_doc import NormalizedDocument


def _normalize_tags(chunk: EvidenceChunk, doc: NormalizedDocument | None) -> list[str]:
    tags = list(chunk.topic_tags)
    if doc:
        extra = infer_topic_tags(doc.title, doc.clean_text)
        for t in extra:
            if t not in tags:
                tags.append(t)
    # stable unique order
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        tt = str(t).strip()
        if tt and tt not in seen:
            seen.add(tt)
            out.append(tt)
    return out


def build_evidence_index(
    chunks: list[EvidenceChunk],
    docs: list[NormalizedDocument],
) -> list[EvidenceIndexItem]:
    by_doc: dict[str, NormalizedDocument] = {d.doc_id: d for d in docs}
    out: list[EvidenceIndexItem] = []
    for ch in chunks:
        doc = by_doc.get(ch.doc_id)
        source_table = doc.source_table if doc else str(ch.metadata.get("source_table", "unknown"))
        stype = default_source_type_for_table(source_table) if doc else ch.source_type
        ev_type = infer_evidence_type(source_table, doc.title if doc else None, ch.text)
        stance = infer_stance_hint(ch, doc, source_table=source_table)
        cred = credibility_score(source_table=source_table, source_type=stype)
        q = quality_score(ch, doc, base_quality=ch.quality_score)
        tags = _normalize_tags(ch, doc)
        cite = build_citation(doc, ch) if doc else f"doc_id={ch.doc_id} | chunk_id={ch.chunk_id}"
        eid = f"ev:{ch.chunk_id}"
        meta = dict(ch.metadata)
        meta.setdefault("evidence_type_resolved", ev_type)
        meta.setdefault("source_table", source_table)
        out.append(
            EvidenceIndexItem(
                evidence_id=eid,
                chunk_id=ch.chunk_id,
                doc_id=ch.doc_id,
                text=ch.text,
                title=doc.title if doc else None,
                source_type=stype,
                evidence_type=ev_type,
                topic_tags=tags,
                stance_hint=stance,
                citation=cite,
                quality_score=q,
                credibility_score=cred,
                metadata=meta,
            )
        )
    return out
