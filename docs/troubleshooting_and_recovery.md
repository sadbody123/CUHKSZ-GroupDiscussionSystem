# Troubleshooting and recovery (local)

## Readiness blocked

Run `python main.py audit-release-readiness --profile-id v1_demo` and fix **error**-severity checks (env, missing snapshot, etc.).

## Consistency warnings on sessions

Stale `speech_report_id`, `mode_report_id`, or learner dirs usually mean a partially written session. Either re-run the feature path or delete the orphan session JSON under the configured session storage directory.

## RC `no_go`

Check `build-rc-report` output: blocked readiness, consistency errors, or failed E2E runs in `latest_e2e.json` under `storage/stability/e2e_results/`.

## API vs CLI mismatch

Both should use `StabilityService`. If results differ, confirm the API is using the same `AppConfig` / snapshot roots as the CLI process.
