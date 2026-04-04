"""Validate snapshot directory structure and JSONL readability."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from app.schemas.evidence import EvidenceChunk
from app.schemas.evidence_index import EvidenceIndexItem
from app.schemas.normalized_doc import NormalizedDocument
from app.schemas.pedagogy import PedagogyItem
from app.schemas.snapshot import SnapshotManifest
from app.schemas.source import SourceRecord
from app.schemas.topic_card import TopicCard


@dataclass
class ValidationResult:
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.ok = False
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


CORE_FILES = (
    "manifest.json",
    "build_report.json",
    "normalized_docs.jsonl",
    "evidence_chunks.jsonl",
    "source_catalog.jsonl",
)

PHASE2_FILES = (
    "pedagogy_items.jsonl",
    "topic_cards.jsonl",
    "evidence_index.jsonl",
)


def _read_jsonl(path: Path, model: type) -> tuple[int, list[str]]:
    errs: list[str] = []
    n = 0
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                model.model_validate(raw)
                n += 1
            except (json.JSONDecodeError, ValidationError) as e:
                errs.append(f"{path.name}:{i}: {e}")
    return n, errs


def _requires_phase2_files(data: dict) -> bool:
    ver = str(data.get("schema_version", "1.0"))
    if ver != "1.0":
        return True
    return bool(
        (data.get("pedagogy_item_count") or 0) > 0
        or (data.get("topic_card_count") or 0) > 0
        or (data.get("evidence_index_count") or 0) > 0
    )


def validate_snapshot_dir(snapshot_dir: Path) -> ValidationResult:
    res = ValidationResult()
    if not snapshot_dir.is_dir():
        res.add_error(f"Not a directory: {snapshot_dir}")
        return res

    for name in CORE_FILES:
        p = snapshot_dir / name
        if not p.is_file():
            res.add_error(f"Missing file: {name}")

    manifest_data: dict = {}
    mf = snapshot_dir / "manifest.json"
    if mf.is_file():
        try:
            manifest_data = json.loads(mf.read_text(encoding="utf-8"))
            SnapshotManifest.model_validate(manifest_data)
        except (json.JSONDecodeError, ValidationError) as e:
            res.add_error(f"manifest.json invalid: {e}")
            manifest_data = {}

    require_p2 = _requires_phase2_files(manifest_data)
    if require_p2:
        for name in PHASE2_FILES:
            if not (snapshot_dir / name).is_file():
                res.add_error(f"Missing file (phase 2 snapshot): {name}")

    for jlpath, model in (
        ("normalized_docs.jsonl", NormalizedDocument),
        ("evidence_chunks.jsonl", EvidenceChunk),
        ("source_catalog.jsonl", SourceRecord),
    ):
        p = snapshot_dir / jlpath
        if not p.is_file():
            continue
        n, errs = _read_jsonl(p, model)
        for e in errs[:20]:
            res.add_error(e)
        if n == 0 and jlpath != "source_catalog.jsonl":
            res.add_warning(f"{jlpath} has zero valid lines")

    for name, model in (
        ("pedagogy_items.jsonl", PedagogyItem),
        ("topic_cards.jsonl", TopicCard),
        ("evidence_index.jsonl", EvidenceIndexItem),
    ):
        p = snapshot_dir / name
        if not p.is_file():
            continue
        n, errs = _read_jsonl(p, model)
        for e in errs[:20]:
            res.add_error(e)
        if n == 0 and require_p2:
            res.add_warning(f"{name} has zero valid lines")

    return res
