"""Load offline snapshot directories into typed in-memory structures."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from app.schemas.evidence import EvidenceChunk
from app.schemas.evidence_index import EvidenceIndexItem
from app.schemas.normalized_doc import NormalizedDocument
from app.schemas.pedagogy import PedagogyItem
from app.schemas.snapshot import BuildReport, SnapshotManifest
from app.schemas.source import SourceRecord
from app.schemas.topic_card import TopicCard

CORE_FILES = (
    "manifest.json",
    "build_report.json",
    "normalized_docs.jsonl",
    "evidence_chunks.jsonl",
    "source_catalog.jsonl",
)


@dataclass
class SnapshotBundle:
    """In-memory view of a snapshot directory."""

    path: Path
    manifest: SnapshotManifest
    build_report: BuildReport
    normalized_docs: list[NormalizedDocument] = field(default_factory=list)
    evidence_chunks: list[EvidenceChunk] = field(default_factory=list)
    source_catalog: list[SourceRecord] = field(default_factory=list)
    pedagogy_items: list[PedagogyItem] = field(default_factory=list)
    topic_cards: list[TopicCard] = field(default_factory=list)
    evidence_index: list[EvidenceIndexItem] = field(default_factory=list)


def _read_jsonl(path: Path, model: type) -> list:
    out: list = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            out.append(model.model_validate(raw))
    return out


def load_snapshot(
    snapshot_dir: Path,
    *,
    require_phase2: bool | None = None,
) -> SnapshotBundle:
    """
    Load snapshot from ``snapshot_dir``.

    :param require_phase2: If True, require pedagogy/topic/evidence_index files.
        If None, infer from manifest (schema_version != 1.0 or warehouse counts > 0).
    """
    root = snapshot_dir.resolve()
    missing = [n for n in CORE_FILES if not (root / n).is_file()]
    if missing:
        raise FileNotFoundError(f"Snapshot missing required files: {missing}")

    manifest = SnapshotManifest.model_validate(
        json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    )
    build_report = BuildReport.model_validate(
        json.loads((root / "build_report.json").read_text(encoding="utf-8"))
    )

    docs = _read_jsonl(root / "normalized_docs.jsonl", NormalizedDocument)
    chunks = _read_jsonl(root / "evidence_chunks.jsonl", EvidenceChunk)
    sources = _read_jsonl(root / "source_catalog.jsonl", SourceRecord)

    need_p2 = require_phase2
    if need_p2 is None:
        need_p2 = manifest.schema_version != "1.0" or (
            (manifest.pedagogy_item_count or 0) + (manifest.topic_card_count or 0) + (manifest.evidence_index_count or 0)
            > 0
        )

    pedagogy: list[PedagogyItem] = []
    topics: list[TopicCard] = []
    evidx: list[EvidenceIndexItem] = []

    p_ped = root / "pedagogy_items.jsonl"
    p_top = root / "topic_cards.jsonl"
    p_evi = root / "evidence_index.jsonl"

    if need_p2:
        for p, label in ((p_ped, "pedagogy_items.jsonl"), (p_top, "topic_cards.jsonl"), (p_evi, "evidence_index.jsonl")):
            if not p.is_file():
                raise FileNotFoundError(f"Phase-2 snapshot missing {label}")
        pedagogy = _read_jsonl(p_ped, PedagogyItem)
        topics = _read_jsonl(p_top, TopicCard)
        evidx = _read_jsonl(p_evi, EvidenceIndexItem)
    else:
        if p_ped.is_file():
            try:
                pedagogy = _read_jsonl(p_ped, PedagogyItem)
            except (OSError, json.JSONDecodeError, ValidationError):
                pedagogy = []
        if p_top.is_file():
            try:
                topics = _read_jsonl(p_top, TopicCard)
            except (OSError, json.JSONDecodeError, ValidationError):
                topics = []
        if p_evi.is_file():
            try:
                evidx = _read_jsonl(p_evi, EvidenceIndexItem)
            except (OSError, json.JSONDecodeError, ValidationError):
                evidx = []

    return SnapshotBundle(
        path=root,
        manifest=manifest,
        build_report=build_report,
        normalized_docs=docs,
        evidence_chunks=chunks,
        source_catalog=sources,
        pedagogy_items=pedagogy,
        topic_cards=topics,
        evidence_index=evidx,
    )
