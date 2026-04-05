# Index artifacts

Indexes live at:

`snapshots/<snapshot_id>/indexes/manifest.json` plus per-store folders (`evidence/`, `pedagogy/`, `topics/`).

**Bundles**: `export_snapshot_bundle` includes the whole `indexes/` tree when present; `bundle_manifest.json` metadata includes `includes_indexes`.

No external vector database is used — only local files under the snapshot directory.
