# Validation, preview, and publish

## Validation

- `AuthoringService.validate_draft` / CLI `validate-draft` / API `POST /authoring/drafts/{id}/validate` run `app/authoring/engines/validator.py` plus `lint_rules.py` per artifact type.
- Output is a `ValidationReport` persisted under `storage/authoring/validation_reports/`.
- `REQUIRE_VALIDATION_BEFORE_PUBLISH` (default true) blocks publish when the latest validation has errors.

## Preview

- Deterministic sandbox in `preview_runner.py`; does not mutate learner/session stores.
- Kinds include `artifact_render`, `launch_spec`, `pack_walkthrough`, `drill_preview`, `retrieval_preview`, `feedback_preview` (some are minimal stubs).
- `ENABLE_AUTHORING_PREVIEW` can disable preview entry points.

## Publish

- `publisher.py` writes only to custom paths; rejects curriculum `pack_id` matching a built-in id and runtime `profile_id` matching a built-in profile stem.
- Produces a `PublicationRecord` under `storage/authoring/publications/`.
- `REQUIRE_PREVIEW_BEFORE_PUBLISH` (default false) can require `draft.status == previewed` before publish.
