# Final acceptance checklist (V1)

Use this before a demo, handoff, or defense. All items are **local** (no external DB, no mandatory cloud APIs).

## 1. Configuration

- [ ] `validate-env` passes or only expected warnings documented.
- [ ] `ACTIVE_RELEASE_PROFILE` matches the intended demo (`v1_demo` typical).
- [ ] `ENABLE_RELEASE_GATING` matches expectations (on for production-like demos).

## 2. Readiness

- [ ] `audit-release-readiness --profile-id <profile>` returns `ready` or `warning` with understood causes (not `blocked` unless acceptable).

## 3. Capability matrix

- [ ] `show-capability-matrix --profile-id <profile>` shows expected enabled/disabled/experimental flags.

## 4. Demo scenarios

- [ ] `text_core_demo` completes successfully with mock provider.
- [ ] Optional: `learner_assignment_demo`, `review_calibration_demo` per profile.

## 5. Regression

- [ ] `pytest` passes.
- [ ] Eval suite `tests/fixtures/evals/suites/release_finalization_suite.yaml` passes when run via project eval runner.

## 6. API / UI

- [ ] `GET /system/capabilities` and `GET /system/readiness` respond.
- [ ] Streamlit sidebar **Release / readiness** expander shows profile and readiness (if API up).

## 7. Artifacts

- [ ] Readiness JSON and demo bundle outputs land under configured `storage/release/` paths without permission errors.
