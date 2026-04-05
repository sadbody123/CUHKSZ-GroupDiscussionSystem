"""Copy documentation into a bundle directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.handover.config import project_root


DEFAULT_DOCS: list[str] = [
    "QUICKSTART.md",
    "DEMO_SCRIPT.md",
    "HANDOVER.md",
    "RELEASE_NOTES.md",
    "KNOWN_LIMITATIONS_FINAL.md",
    "docs/final_delivery_overview.md",
    "docs/demo_kit_spec.md",
    "docs/acceptance_evidence_spec.md",
    "docs/final_runbook.md",
    "docs/architecture_at_a_glance.md",
]


def export_docs_bundle(output_dir: Path, *, profile_id: str) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    root = project_root()
    copied: list[str] = []
    for rel in DEFAULT_DOCS:
        src = root / rel
        if not src.is_file():
            continue
        dst = output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)
    (output_dir / "bundle_profile.txt").write_text(profile_id + "\n", encoding="utf-8")
    copied.append("bundle_profile.txt")
    return copied
