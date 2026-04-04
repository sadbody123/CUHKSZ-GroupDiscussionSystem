# Session replay (phase 6)

## Modes

| Mode | Behavior |
|------|----------|
| `analyze` | Re-run `analyze_transcript_turns` with the selected profile’s analyzer section; writes `replay_summary.json`. |
| `plan-turn` | Load snapshot, build `SessionStateMachine` with profile orchestration, `peek_next_role` for the export’s last turn. |
| `full-mock` | Run a minimal `e2e_case`-style flow via `e2e_runner` (mock provider, temp session dir). |

## CLI

```bash
python main.py replay-session \
  --session-file tests/fixtures/evals/sessions/sample_session_export.json \
  --mode analyze \
  --profile-id strict_coach \
  --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 \
  --output-dir tmp/replay/out
```

`app/evals/replay/comparators.py` offers small helpers for signal set diffs when building custom tooling.
