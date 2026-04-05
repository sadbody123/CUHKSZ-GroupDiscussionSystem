# Snapshot bundle format

A **snapshot bundle** is a zip file produced from an existing validated snapshot directory. It does **not** change the on-disk snapshot layout used by `snapshot_loader`; it only packages those files for transport.

## Layout (zip root)

| Path | Purpose |
|------|---------|
| `bundle_manifest.json` | Metadata (ids, versions, file list, checksum map). |
| `checksums.sha256` | One line per file: `<sha256>  <relative/path>` (paths use `/`). |
| `snapshot/` | Copy of snapshot files (see below). |

## Snapshot payload files

At minimum, the exporter includes files that exist under the source directory from this allowlist:

- `manifest.json`, `build_report.json`
- `normalized_docs.jsonl`, `evidence_chunks.jsonl`, `source_catalog.jsonl`
- `pedagogy_items.jsonl`, `topic_cards.jsonl`, `evidence_index.jsonl` (when present)

The source directory must pass `validate_snapshot_dir()` before export.

## `bundle_manifest.json` fields

| Field | Description |
|-------|-------------|
| `bundle_id` | UUID for this bundle build. |
| `created_at` | ISO-8601 UTC timestamp. |
| `app_version` | Package / app version string. |
| `snapshot_id` | From `manifest.json` (`snapshot_id` or folder name). |
| `schema_version` | Bundle schema version (currently `1.0`). |
| `included_files` | Paths included in the zip. |
| `checksums` | Map of relative path → sha256 hex (snapshot files only). |
| `metadata` | Free-form (e.g. `exported_from`). |

## Checksums

- SHA-256 of file bytes.
- `checksums.sha256` lists **`snapshot/...`** entries; it is generated after files are staged.

## Import

1. Extract zip to a temporary directory.
2. Read and validate `bundle_manifest.json`.
3. Verify every entry in `checksums.sha256`.
4. Copy `snapshot/` into `SNAPSHOT_ROOT/<target_id>/`.
5. **Rename conflict policy** (`--on-conflict`): `fail` | `overwrite` | `rename` (folder `__importN`); if the folder name differs from embedded `snapshot_id`, `manifest.json` is patched so `snapshot_id` matches the folder name.
