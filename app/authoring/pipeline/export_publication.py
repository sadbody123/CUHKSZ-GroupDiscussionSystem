"""Export published artifact to a single JSON file."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.authoring.store.publication_store import PublicationStore


def export_publication_json(
    store: PublicationStore,
    publication_id: str,
    output_file: Path,
) -> Path:
    rec = store.load_publication_record(publication_id)
    if not rec:
        raise ValueError("publication not found")
    payload = store.load_published_artifact_payload(rec)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    bundle = {"publication": rec.model_dump(), "payload": payload}
    output_file.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_file


def export_publication_zip(source_dir: Path, output_zip: Path) -> Path:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    shutil.make_archive(str(output_zip.with_suffix("")), "zip", root_dir=source_dir)
    # make_archive adds .zip
    z = output_zip if output_zip.suffix == ".zip" else Path(str(output_zip) + ".zip")
    return z if z.is_file() else output_zip
