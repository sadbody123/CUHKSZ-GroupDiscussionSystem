# Review workspace and manual calibration

The review workspace lets local **reviewer profiles** audit session outputs: coach feedback, optional speech/mode/group artifacts, and learner summaries. It is **not** a formal grading or authentication system.

## Flow

1. Complete a discussion session and generate feedback (coach report).
2. Create a **review pack** for the session (aggregates references and summaries).
3. Submit a **human review** (rubric scores, annotations, optional approved overrides).
4. The system generates a **calibration report** comparing AI-highlighted strengths/risks with human notes (training calibration only).

## Settings

See `ENABLE_REVIEW_WORKSPACE`, `REVIEW_STORAGE_DIR`, `REVIEWER_STORAGE_DIR`, `AUTO_CREATE_REVIEW_PACK_AFTER_FEEDBACK`, `ENABLE_OVERRIDE_MERGE`, and `CALIBRATION_DELTA_WARN_THRESHOLD` in `app/ops/settings.py`.

## CLI and API

- CLI: `create-reviewer`, `create-review-pack`, `submit-review`, `compare-ai-vs-human`, `export-calibration-report`, `export-reviewed-feedback`.
- API: `/reviewers`, `/review-packs`, `/sessions/{id}/review-pack`, `/sessions/{id}/review-summary`, `/sessions/{id}/calibration`.
