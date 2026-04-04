"""Topic card loading and bootstrap tests."""

from __future__ import annotations

from pathlib import Path

from app.offline_build.topic_cards.bootstrap import bootstrap_topic_cards, merge_topic_cards
from app.offline_build.topic_cards.loader import load_topic_card_directory
from app.schemas.evidence import EvidenceChunk


def test_load_manual_topic_cards(fixture_topic_cards_dir: Path) -> None:
    cards, nfiles = load_topic_card_directory(fixture_topic_cards_dir)
    assert nfiles >= 1
    assert len(cards) >= 1
    assert cards[0].topic_id


def test_bootstrap_without_manual(tmp_path: Path) -> None:
    chunks = [
        EvidenceChunk(
            chunk_id="c1",
            doc_id="d1",
            text="x" * 200,
            source_type="community",
            evidence_type="article",
            topic_tags=["ai", "research"],
            citation=None,
            quality_score=0.5,
            metadata={},
        )
    ]
    boot = bootstrap_topic_cards(chunks, manual=[], top_n=5, max_hints=2)
    assert len(boot) >= 1
    merged = merge_topic_cards([], boot)
    assert len(merged) == len(boot)
