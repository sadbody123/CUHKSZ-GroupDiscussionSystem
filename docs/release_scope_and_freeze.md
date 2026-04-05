# V1 release scope and freeze

This document describes how **CUHKSZ-GroupDiscussionSystem** is scoped for a deliverable V1 baseline. It is **not** a product roadmap; it reflects the repository’s release profiles, capability registry, and automated scope-freeze output.

## Scope principles

- **Upstream boundary**: raw crawling and export live in `CUHKSZ-Datahub`; this repo consumes **snapshots** only.
- **No parallel runtimes**: release/demo tooling calls **existing** `SessionService`, `LearnerService`, `CurriculumService`, `ReviewService`, etc., via `app/release/engines/scenario_runner.py`.
- **Gating over deletion**: capabilities may be **disabled or hidden by profile** without removing code.

## Freeze mechanics

- **Profiles**: YAML under `app/release/profiles/` (`v1_minimal`, `v1_demo`, `v1_full_local`).
- **Registry**: `app/release/engines/capability_registry.py` lists capabilities with stability and dependencies.
- **Scope summary**: `build_scope_freeze_summary()` in `app/release/engines/scope_freezer.py` classifies each capability for the active profile (`keep`, `hide_by_default`-style decisions via `DECISION_*` constants).
- **CLI**: `python main.py freeze-scope-report --profile-id v1_demo` writes a JSON report under the configured release report directory.

## Deviation from aspirational docs

If a capability is marked **beta** or **experimental** in the registry, that reflects **current implementation confidence**, not a permanent product label. Re-run `show-capability-matrix` after major changes.
