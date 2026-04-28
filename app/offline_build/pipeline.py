"""End-to-end offline build pipeline."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings, get_settings
from app.offline_build.adapters.registry import get_adapter
from app.offline_build.build_snapshot.manifest import build_manifest
from app.offline_build.build_snapshot.writer import write_snapshot
from app.offline_build.chunk.evidence_chunker import chunk_document
from app.offline_build.classify.source_type import default_source_type_for_table
from app.offline_build.dedupe.exact import dedupe_by_text_hash
from app.offline_build.dedupe.near_dup import NearDupDetector
from app.offline_build.evidence_index.builder import build_evidence_index
from app.offline_build.import_datahub.export_locator import locate_exports
from app.offline_build.import_datahub.loader import load_table_file
from app.offline_build.normalize.language_utils import guess_language_hint
from app.offline_build.normalize.metadata_normalizer import normalize_metadata
from app.offline_build.normalize.text_cleaner import clean_text, is_low_value_text
from app.offline_build.pedagogy.loader import load_pedagogy_directory
from app.offline_build.topic_cards.bootstrap import bootstrap_topic_cards, merge_topic_cards
from app.offline_build.topic_cards.loader import load_topic_card_directory
from app.schemas.evidence import EvidenceChunk
from app.schemas.normalized_doc import NormalizedDocument
from app.schemas.snapshot import BuildReport
from app.schemas.source import SourceRecord


def run_offline_pipeline(
    input_dir: Path,
    snapshot_id: str,
    settings: Settings | None = None,
    *,
    snapshot_root: Path | None = None,
    pedagogy_dir: Path | None = None,
    topic_card_dir: Path | None = None,
) -> Path:
    """
    Import exports → normalize → dedupe → chunk → write snapshot.

    When ``pedagogy_dir`` or ``topic_card_dir`` is set, also builds the three
    knowledge warehouses (pedagogy, topic cards, evidence index) and writes
    ``schema_version`` ``1.1`` artifacts.

    :param snapshot_root: Optional override for output root (e.g. tests).
    """
    cfg = settings or get_settings()
    input_dir = input_dir.resolve()
    root = snapshot_root if snapshot_root is not None else cfg.snapshot_root
    out_dir = (root / snapshot_id).resolve()

    knowledge_mode = pedagogy_dir is not None or topic_card_dir is not None

    exports = locate_exports(input_dir)
    source_catalog: list[SourceRecord] = []
    normalized: list[NormalizedDocument] = []
    records_read = 0
    dropped = 0

    for exp in exports:
        adapter = get_adapter(exp.table_name)
        if adapter is None:
            continue
        rows = load_table_file(exp.path)
        records_read += len(rows)
        source_catalog.append(
            SourceRecord(
                source_table=exp.table_name,
                source_type=default_source_type_for_table(exp.table_name),
                source_file=exp.path.name,
                record_count=len(rows),
                notes=None,
            )
        )
        for row in rows:
            doc = adapter.normalize_record(row, file_name=exp.path.name)
            if doc is None:
                dropped += 1
                continue
            cleaned = clean_text(doc.clean_text)
            if is_low_value_text(cleaned, cfg.min_text_chars):
                dropped += 1
                continue
            doc.clean_text = cleaned
            if not doc.language:
                doc.language = guess_language_hint(cleaned)
            doc.metadata = normalize_metadata(doc.metadata)
            normalized.append(doc)

    pre_dedupe = len(normalized)
    deduped, _dupes = dedupe_by_text_hash(normalized)

    # Near-duplicate detection (SimHash)
    near_dup_removed = 0
    near_dup_cluster_count = 0
    if len(deduped) > 1:
        near_detector = NearDupDetector(
            hash_bits=cfg.near_dup_hash_bits,
            similarity_threshold=cfg.near_dup_threshold,
        )
        clusters = near_detector.find_near_duplicates(deduped)
        near_dup_cluster_count = len(clusters)
        drop_ids: set[str] = set()
        for cluster in clusters:
            drop_ids.update(cluster[1:])
        if drop_ids:
            near_dup_removed = len(drop_ids)
            deduped = [d for d in deduped if d.doc_id not in drop_ids]

    chunks: list[EvidenceChunk] = []
    for doc in deduped:
        chunks.extend(
            chunk_document(
                doc,
                chunk_size=cfg.chunk_size,
                chunk_overlap=cfg.chunk_overlap,
            )
        )

    tables_used = sorted({e.table_name for e in exports})

    build_rep = BuildReport(
        input_file_count=len(exports),
        records_read=records_read,
        normalized_success=pre_dedupe,
        dropped=dropped,
        pre_dedupe_count=pre_dedupe,
        post_dedupe_count=len(deduped),
        near_dup_removed_count=near_dup_removed,
        near_dup_clusters=near_dup_cluster_count,
        chunk_count=len(chunks),
        tables_used=tables_used,
    )

    if not knowledge_mode:
        manifest = build_manifest(
            snapshot_id=snapshot_id,
            input_tables=tables_used,
            normalized_doc_count=len(deduped),
            evidence_chunk_count=len(chunks),
            deduped_doc_count=len(deduped),
            notes=None,
            schema_version="1.0",
        )
        write_snapshot(
            out_dir,
            manifest=manifest,
            build_report=build_rep,
            normalized_docs=deduped,
            evidence_chunks=chunks,
            source_catalog=source_catalog,
        )
        return out_dir

    pedagogy_items: list = []
    ped_files = 0
    ped_lines = 0
    if pedagogy_dir is not None:
        pedagogy_items, ped_files, ped_lines = load_pedagogy_directory(pedagogy_dir.resolve())

    manual_cards, tc_files = load_topic_card_directory(
        topic_card_dir.resolve() if topic_card_dir is not None else None
    )
    boot = bootstrap_topic_cards(chunks, manual=manual_cards, top_n=12, max_hints=3)
    topic_cards = merge_topic_cards(manual_cards, boot)

    evidence_index = build_evidence_index(chunks, deduped)

    build_rep.pedagogy_files_read = ped_files
    build_rep.pedagogy_lines_read = ped_lines
    build_rep.pedagogy_items_out = len(pedagogy_items)
    build_rep.topic_card_files_read = tc_files
    build_rep.topic_cards_manual = len(manual_cards)
    build_rep.topic_cards_bootstrapped = len(boot)
    build_rep.topic_cards_out = len(topic_cards)
    build_rep.evidence_index_count = len(evidence_index)

    manifest = build_manifest(
        snapshot_id=snapshot_id,
        input_tables=tables_used,
        normalized_doc_count=len(deduped),
        evidence_chunk_count=len(chunks),
        deduped_doc_count=len(deduped),
        notes=None,
        pedagogy_item_count=len(pedagogy_items),
        topic_card_count=len(topic_cards),
        evidence_index_count=len(evidence_index),
        schema_version="1.1",
    )

    write_snapshot(
        out_dir,
        manifest=manifest,
        build_report=build_rep,
        normalized_docs=deduped,
        evidence_chunks=chunks,
        source_catalog=source_catalog,
        pedagogy_items=pedagogy_items,
        topic_cards=topic_cards,
        evidence_index=evidence_index,
    )
    return out_dir
