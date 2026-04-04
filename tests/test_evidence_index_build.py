"""Evidence index builder tests."""

from __future__ import annotations

from app.offline_build.evidence_index.builder import build_evidence_index
from app.schemas.evidence import EvidenceChunk
from app.schemas.normalized_doc import NormalizedDocument


def test_evidence_index_enriches_chunks() -> None:
    doc = NormalizedDocument(
        doc_id="reports:1",
        source_table="reports",
        source_id="1",
        title="Official notice",
        url="https://example.edu/n",
        published_at="2025-01-01",
        language="en",
        clean_text="Support the policy because it improves transparency.",
        source_type="official_report",
        raw_record_ref="1",
        metadata={},
    )
    ch = EvidenceChunk(
        chunk_id="reports:1#c0",
        doc_id="reports:1",
        text=doc.clean_text,
        source_type=doc.source_type,
        evidence_type="report",
        topic_tags=["research"],
        citation=None,
        quality_score=0.4,
        metadata={"source_table": "reports"},
    )
    rows = build_evidence_index([ch], [doc])
    assert len(rows) == 1
    r = rows[0]
    assert r.evidence_id.startswith("ev:")
    assert r.credibility_score is not None
    assert r.quality_score is not None
    assert r.stance_hint is not None
    assert r.citation
    assert r.topic_tags
