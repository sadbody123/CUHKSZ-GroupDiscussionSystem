"""Normalization and text cleaning tests."""

from __future__ import annotations

from app.offline_build.adapters.research_projects import ResearchProjectsAdapter
from app.offline_build.normalize.text_cleaner import clean_text, is_low_value_text


def test_clean_text_collapses_whitespace() -> None:
    raw = "  hello   world  \n\n\n  next  "
    out = clean_text(raw)
    assert "hello world" in out
    assert "next" in out


def test_is_low_value_short() -> None:
    assert is_low_value_text("short", min_chars=20) is True
    assert is_low_value_text("x" * 25, min_chars=20) is False


def test_adapter_tolerates_missing_optional_fields() -> None:
    adapter = ResearchProjectsAdapter()
    doc = adapter.normalize_record(
        {
            "id": "p1",
            "title": "Minimal project record with enough characters in the title field alone.",
        },
        file_name="research_projects.json",
    )
    assert doc is not None
    assert doc.url is None
    assert doc.metadata.get("upstream_file") == "research_projects.json"
