# Stability and RC hardening (phase 18)

This phase adds a **stability layer** (`app/stability/`) for:

- Canonical **E2E scenario matrix** (YAML under `app/stability/scenarios/`)
- **Consistency audit** over local session files and release demo scenario refs
- **Issue aggregation** (manual YAML + audit-derived rows)
- **Stability report** and **release candidate report** (advisory go / conditional / no-go)

It does **not** change upstream Datahub boundaries or replace the release readiness pipeline from phase 17.

## Commands

See `docs/release_candidate_runbook.md` for CLI entry points and suggested order.
