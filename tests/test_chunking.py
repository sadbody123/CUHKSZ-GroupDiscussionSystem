"""Evidence chunking tests."""

from __future__ import annotations

from app.offline_build.chunk.evidence_chunker import chunk_document
from app.schemas.normalized_doc import NormalizedDocument


def _doc(text: str) -> NormalizedDocument:
    return NormalizedDocument(
        doc_id="test:1",
        source_table="reports",
        source_id="1",
        title="t",
        url=None,
        published_at=None,
        language="en",
        clean_text=text,
        source_type="official_report",
        raw_record_ref=None,
        metadata={},
    )


def test_short_text_single_chunk() -> None:
    text = "This is a short but valid paragraph for chunking purposes here."
    chunks = chunk_document(_doc(text), chunk_size=600, chunk_overlap=80)
    assert len(chunks) == 1
    assert chunks[0].doc_id == "test:1"


def test_long_text_multiple_chunks() -> None:
    text = ("Paragraph block. " * 80).strip()
    chunks = chunk_document(_doc(text), chunk_size=120, chunk_overlap=20)
    assert len(chunks) >= 3
