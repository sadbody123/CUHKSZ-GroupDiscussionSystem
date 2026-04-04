"""Tests for export discovery and loading."""

from __future__ import annotations

from pathlib import Path

from app.offline_build.adapters.registry import get_adapter
from app.offline_build.import_datahub.export_locator import locate_exports
from app.offline_build.import_datahub.loader import load_table_file


def test_locate_exports_finds_fixture_tables(fixture_exports_dir: Path) -> None:
    found = locate_exports(fixture_exports_dir)
    names = {e.table_name for e in found}
    assert "reports" in names
    assert "research_outputs" in names
    assert len(found) >= 8


def test_load_json_and_adapter(fixture_exports_dir: Path) -> None:
    p = fixture_exports_dir / "reports.json"
    rows = load_table_file(p)
    assert len(rows) >= 1
    adapter = get_adapter("reports")
    assert adapter is not None
    doc = adapter.normalize_record(rows[0], file_name=p.name)
    assert doc is not None
    assert doc.source_table == "reports"
    assert len(doc.clean_text) >= 20
