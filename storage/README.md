# Runtime storage layout

This directory holds **local, machine-generated** JSON and reports (sessions, learners, reviews, handover bundles, stability outputs, etc.).

## What is safe to delete

- **Session JSON** under `sessions/*.json` — safe to remove if you do not need old demos (the API/CLI will create new ones).
- **Eval / feedback / bundle outputs** — regenerable from CLI commands.
- **Per-feature subfolders** (`learners/`, `reviews/`, `handover/`, …) — delete only if you accept losing local history for that feature.

## Git strategy

- **`.gitignore`** ignores most generated artifacts (e.g. `storage/sessions/*.json`, built snapshots under `app/knowledge/snapshots/*/`).  
- **Sample or pinned demo files** may be force-added for CI or handover; treat them as **fixtures**, not source code.  
- Prefer **`python main.py bootstrap-dev-snapshot`** to recreate `dev_snapshot_v2` instead of committing large binary trees.

## Do not commit

Secrets (`.env`), personal learner data, or large audio blobs unless you intend to share them as curated fixtures.
