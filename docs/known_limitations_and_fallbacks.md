# Known limitations and fallbacks

## Accepted limitations

Manual entries can be recorded under `storage/stability/issues/issues.yaml` (or `tests/fixtures/stability/known_issues/issues.yaml` for regression). Use `status: accepted_limitation` and a `reason` in metadata.

## Recovery policies

See `app/stability/engines/recovery_policy.py` for deterministic descriptions of degraded behavior (text-only, gated capabilities, etc.). This is **documentation + lookup**, not automatic repair of corrupted files.
