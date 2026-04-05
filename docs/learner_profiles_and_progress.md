# Learner profiles and progress

Phase 11 adds **local-only** learner identifiers (`learner_id`) and a file-backed store under `storage/learners/` (configurable via `LEARNER_STORAGE_DIR`).

- **Profile** aggregates weak/strong/focus skills from heuristic transcript signals and optional speech proxy metrics.
- **Timeline** stores one **ProgressPoint** per ingested session.
- Sessions can be linked at creation time or via **attach**; ingest is **idempotent** on the timeline.

Skill scores are **training heuristics**, not exam grades. Speech-related dimensions are explicitly **proxy** metrics with disclaimers in API/UI.
