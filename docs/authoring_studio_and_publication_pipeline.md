# Authoring Studio and Publication Pipeline (Phase 16)

## Purpose

Phase 16 adds a **local, file-backed** layer for drafting, validating, previewing, and publishing **custom** training content. It does not replace Datahub ingestion or offline snapshot builds; it sits beside curriculum packs, modes, and review outputs as a **curation and delivery** path.

## Layout

- **Authoring root**: `AUTHORING_ROOT_DIR` (default `storage/authoring/`)
  - `drafts/` — JSON drafts
  - `patches/` — patch proposals
  - `publications/` — publication records
  - `validation_reports/`, `preview_results/` — saved reports
  - `published/` — published artifacts by type (e.g. `runtime_profiles/`, `artifacts/`)
- **Curriculum custom packs**: still written under `CURRICULUM_CUSTOM_PACK_DIR` (JSON). Publishing a `curriculum_pack` draft uses `PackStore.save_custom_pack`; **built-in YAML packs are never modified**.

## Entry points

- **CLI**: `python main.py list-authorable-artifacts`, `create-draft`, `create-blank-draft`, `validate-draft`, `preview-draft`, `publish-draft`, patch commands, `export-authored-artifact`, etc.
- **API**: `/authoring/*` routes (see OpenAPI).
- **UI**: Streamlit expander **Authoring Studio** (calls API via `DiscussionApiClient`).

## Smoke

```text
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --with-authoring
```

## Eval

```text
python main.py run-evals --suite-file tests/fixtures/evals/suites/authoring_publication_suite.yaml --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 --profile-id default --output-dir tmp/eval_reports/authoring_publication
```

## Non-goals

No database, no multi-user CMS, no silent overwrite of built-in assets. Review and learner analytics feed **patch proposals** only; applying patches is explicit.

## Related docs

- `docs/authorable_artifact_spec.md` — types and storage layout
- `docs/validation_preview_and_publish.md` — gates and flags
- `docs/review_to_patch_and_curriculum_curation.md` — review/learner → patch workflow
