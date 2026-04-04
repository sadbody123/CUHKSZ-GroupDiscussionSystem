"""Phase-2 snapshot build and validation."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.offline_build.build_snapshot.validators import validate_snapshot_dir
from app.offline_build.pipeline import run_offline_pipeline


def test_knowledge_snapshot_has_three_warehouses(
    fixture_exports_dir: Path,
    fixture_pedagogy_dir: Path,
    fixture_topic_cards_dir: Path,
    tmp_path: Path,
) -> None:
    settings = Settings.from_env()
    out = run_offline_pipeline(
        fixture_exports_dir,
        "v2_test",
        settings=settings,
        snapshot_root=tmp_path,
        pedagogy_dir=fixture_pedagogy_dir,
        topic_card_dir=fixture_topic_cards_dir,
    )
    for name in (
        "pedagogy_items.jsonl",
        "topic_cards.jsonl",
        "evidence_index.jsonl",
    ):
        assert (out / name).is_file()

    mf = (out / "manifest.json").read_text(encoding="utf-8")
    assert "1.1" in mf
    br = (out / "build_report.json").read_text(encoding="utf-8")
    assert "pedagogy_items_out" in br

    res = validate_snapshot_dir(out)
    assert res.ok, res.errors
