"""Character-based chunking with overlap."""

from __future__ import annotations

from app.offline_build.classify.evidence_type import infer_evidence_type
from app.offline_build.classify.topic_tags import infer_topic_tags
from app.schemas.evidence import EvidenceChunk
from app.schemas.normalized_doc import NormalizedDocument


def _chunks_from_text(text: str, size: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    out: list[str] = []
    step = max(1, size - overlap)
    i = 0
    while i < len(text):
        piece = text[i : i + size]
        out.append(piece.strip())
        if i + size >= len(text):
            break
        i += step
    return [c for c in out if c]


def chunk_document(
    doc: NormalizedDocument,
    *,
    chunk_size: int = 600,
    chunk_overlap: int = 80,
) -> list[EvidenceChunk]:
    """Split document text into evidence chunks."""
    evidence_type = infer_evidence_type(doc.source_table, doc.title, doc.clean_text)
    tags = infer_topic_tags(doc.title, doc.clean_text)
    parts = _chunks_from_text(doc.clean_text, chunk_size, chunk_overlap)
    if not parts:
        return []

    chunks: list[EvidenceChunk] = []
    for idx, part in enumerate(parts):
        cid = f"{doc.doc_id}#c{idx}"
        citation = doc.title or doc.url or doc.doc_id
        chunks.append(
            EvidenceChunk(
                chunk_id=cid,
                doc_id=doc.doc_id,
                text=part,
                source_type=doc.source_type,
                evidence_type=evidence_type,
                topic_tags=tags,
                citation=citation,
                quality_score=None,
                metadata={
                    "chunk_index": idx,
                    "chunk_count": len(parts),
                    "source_table": doc.source_table,
                },
            )
        )
    return chunks
