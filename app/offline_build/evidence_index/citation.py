"""Stable citation strings for evidence rows."""

from __future__ import annotations

from app.schemas.evidence import EvidenceChunk
from app.schemas.normalized_doc import NormalizedDocument


def build_citation(doc: NormalizedDocument | None, chunk: EvidenceChunk) -> str:
    """Prefer title, URL, date, and source labels for a reproducible citation line."""
    parts: list[str] = []
    title = (doc.title if doc else None) or None
    if title:
        parts.append(str(title).strip())
    url = doc.url if doc else None
    if url:
        parts.append(str(url).strip())
    pub = doc.published_at if doc else None
    if pub:
        parts.append(str(pub).strip())
    st = chunk.source_type
    parts.append(f"source_type={st}")
    if doc:
        parts.append(f"table={doc.source_table}")
    parts.append(f"doc_id={chunk.doc_id}")
    parts.append(f"chunk_id={chunk.chunk_id}")
    return " | ".join(p for p in parts if p)
