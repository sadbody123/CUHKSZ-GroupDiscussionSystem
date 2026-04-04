# Evaluation framework (phase 6)

## Layout

- `app/evals/schemas/` — `EvalCase`, `EvalSuite`, `EvalResult`, `EvalReport`
- `app/evals/loaders/` — suite + case YAML, session export JSON
- `app/evals/runners/` — `retrieval_case`, `state_machine_case`, `analyzer_case`, `agent_case`, `e2e_case`
- `app/evals/run_suite.py` — `run_eval_suite`, `compare_profiles`
- `app/evals/reporters/` — JSON / Markdown / CSV
- `app/evals/replay/` — analyze / plan-turn / full-mock replay summaries
- `app/evals/cli/commands.py` — Typer commands registered on `main.py`

## Case files

Cases live under `tests/fixtures/evals/cases/*.yaml` with a top-level `cases:` list. Suites reference them by `case_id` in `case_refs`.

## Commands

```bash
python main.py run-evals --suite-file tests/fixtures/evals/suites/smoke_suite.yaml \
  --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 \
  --profile-id default --output-dir tmp/eval_reports/smoke

python main.py compare-profiles --suite-file tests/fixtures/evals/suites/regression_suite.yaml \
  --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 \
  --profiles "default balanced concise" --output-dir tmp/eval_reports/cmp
```

All runners reuse existing runtime / application code; **mock** is the default provider for agents and e2e.
