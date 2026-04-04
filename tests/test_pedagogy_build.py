"""Pedagogy KB loading tests."""

from __future__ import annotations

from pathlib import Path

from app.offline_build.pedagogy.loader import load_pedagogy_directory


def test_load_pedagogy_fixtures(fixture_pedagogy_dir: Path) -> None:
    items, files, lines = load_pedagogy_directory(fixture_pedagogy_dir)
    assert files >= 1
    assert lines >= 1
    assert len(items) > 0
    assert all(hasattr(x, "item_id") for x in items)


def test_pedagogy_missing_dir_is_empty() -> None:
    items, files, lines = load_pedagogy_directory(Path("/nonexistent/path/pedagogy"))
    assert items == []
    assert files == 0
