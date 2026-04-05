# Handover (course / maintainer)

This repository is a **downstream consumer** of exported Datahub tables; it does not crawl production sites at runtime.

**Advisory only:** handover kits, BOMs, acceptance evidence, and demo bundles are **engineering / training support** artifacts. They are **not** formal certification or compliance deliverables unless your institution explicitly adopts them as such.

## What to hand over

- Offline snapshot(s) under `app/knowledge/snapshots/` (or your configured `SNAPSHOT_ROOT`)
- Release profile YAML (`app/release/profiles/`, typically `v1_demo`)
- Generated handover assets: `python main.py build-handover-kit --profile-id v1_demo --output-dir tmp/handover_kit`
- Acceptance evidence export: `python main.py export-acceptance-evidence --profile-id v1_demo --output-file tmp/acceptance.md`

## Boundaries

- No database service is required for the default path.
- Known limitations are listed in `KNOWN_LIMITATIONS_FINAL.md` and acceptance exports.
