"""Write snapshot artifacts to disk."""

from __future__ import annotations

from pathlib import Path

from app.schemas.evidence import EvidenceChunk
from app.schemas.evidence_index import EvidenceIndexItem
from app.schemas.normalized_doc import NormalizedDocument
from app.schemas.pedagogy import PedagogyItem
from app.schemas.snapshot import BuildReport, SnapshotManifest
from app.schemas.source import SourceRecord
from app.schemas.topic_card import TopicCard


def _write_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(row.model_dump_json() + "\n")


def _write_json(path: Path, obj: SnapshotManifest | BuildReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj.model_dump_json(indent=2) + "\n", encoding="utf-8")


def write_snapshot(
    out_dir: Path,
    *,
    manifest: SnapshotManifest,
    build_report: BuildReport,
    normalized_docs: list[NormalizedDocument],
    evidence_chunks: list[EvidenceChunk],
    source_catalog: list[SourceRecord],
    pedagogy_items: list[PedagogyItem] | None = None,
    topic_cards: list[TopicCard] | None = None,
    evidence_index: list[EvidenceIndexItem] | None = None,
) -> None:
    """
    Write core snapshot files.

    When ``pedagogy_items`` / ``topic_cards`` / ``evidence_index`` are not ``None``,
    phase-2 files are written (lists may be empty).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "manifest.json", manifest)
    _write_json(out_dir / "build_report.json", build_report)
    _write_jsonl(out_dir / "normalized_docs.jsonl", normalized_docs)
    _write_jsonl(out_dir / "evidence_chunks.jsonl", evidence_chunks)
    _write_jsonl(out_dir / "source_catalog.jsonl", source_catalog)
    if pedagogy_items is not None:
        _write_jsonl(out_dir / "pedagogy_items.jsonl", pedagogy_items)
    if topic_cards is not None:
        _write_jsonl(out_dir / "topic_cards.jsonl", topic_cards)
    if evidence_index is not None:
        _write_jsonl(out_dir / "evidence_index.jsonl", evidence_index)
