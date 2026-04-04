"""End-to-end snapshot build tests."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.offline_build.build_snapshot.validators import validate_snapshot_dir
from app.offline_build.pipeline import run_offline_pipeline


def test_build_offline_writes_artifacts(fixture_exports_dir: Path, tmp_path: Path) -> None:
    settings = Settings.from_env()
    settings.min_text_chars = 20
    out = run_offline_pipeline(
        fixture_exports_dir,
        "pytest_snapshot",
        settings=settings,
        snapshot_root=tmp_path,
    )
    assert out.is_dir()
    for name in (
        "manifest.json",
        "build_report.json",
        "normalized_docs.jsonl",
        "evidence_chunks.jsonl",
        "source_catalog.jsonl",
    ):
        assert (out / name).is_file()

    manifest = (out / "manifest.json").read_text(encoding="utf-8")
    assert "pytest_snapshot" in manifest

    nd_lines = [
        ln
        for ln in (out / "normalized_docs.jsonl").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert len(nd_lines) > 0

    res = validate_snapshot_dir(out)
    assert res.ok, res.errors
