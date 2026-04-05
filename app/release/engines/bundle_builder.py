"""Build demo bundle directory / zip."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.release.engines.report_builder import build_capability_matrix_markdown
from app.release.pipeline.build_capability_matrix import build_capability_matrix_json
from app.release.schemas.bundle import DemoBundleManifest


def build_demo_bundle(
    *,
    profile_id: str,
    output_dir: Path,
    readiness_report: dict[str, Any] | None,
    scenario_results: list[dict[str, Any]] | None,
    scope_summary: dict[str, Any] | None,
) -> DemoBundleManifest:
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    bid = f"bundle_{uuid.uuid4().hex[:10]}"

    (output_dir / "capability_matrix.json").write_text(
        json.dumps(build_capability_matrix_json(profile_id), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "capability_matrix.md").write_text(build_capability_matrix_markdown(profile_id), encoding="utf-8")

    if readiness_report:
        (output_dir / "readiness_report.json").write_text(
            json.dumps(readiness_report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    sr_dir = output_dir / "scenario_results"
    sr_dir.mkdir(exist_ok=True)
    for i, r in enumerate(scenario_results or []):
        (sr_dir / f"scenario_{i}.json").write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if scope_summary:
        (output_dir / "scope_freeze_summary.json").write_text(
            json.dumps(scope_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    man = DemoBundleManifest(
        bundle_id=bid,
        profile_id=profile_id,
        created_at=now,
        included_reports=["readiness_report.json"] if readiness_report else [],
        included_scenarios=[f"scenario_{i}" for i in range(len(scenario_results or []))],
        included_artifacts=["capability_matrix.json", "capability_matrix.md"],
        output_paths={"root": str(output_dir.resolve())},
        notes=["Demo bundle for local delivery; not a snapshot bundle."],
        metadata={},
    )
    (output_dir / "manifest.json").write_text(json.dumps(man.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return man


def zip_bundle(source_dir: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    base = zip_path.with_suffix("")
    shutil.make_archive(str(base), "zip", root_dir=source_dir)
    out = Path(str(base) + ".zip")
    return out if out.is_file() else zip_path
