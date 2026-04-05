# Review → patch → curriculum curation

## Data flow (training aids only)

1. **Review packs** / calibration / learner profiles / curriculum gaps can feed **patch proposals** via `generate_patch_proposals` (`patch_generator.py`).
2. Each `PatchProposal` includes `reason`, `evidence_refs`, and `proposed_ops`; metadata may carry `proxy_note` limitations.
3. Patches are **not** auto-applied to published content. Use `apply_patch_to_draft` explicitly, then validate → preview → publish.

## Curriculum integration

- Published custom packs appear in `PackStore.list_packs` / API `GET /curriculum-packs` alongside built-ins (custom JSON takes precedence at load time when present — **authoring enforces new ids** to avoid silent shadowing of built-in filenames).
- Assignments and sessions can reference `curriculum_pack_id` that resolves to a custom published pack.

## Limitations

- Reviewed outputs and learner analytics remain **non-official** signals; they inform curation, not institutional grades.
