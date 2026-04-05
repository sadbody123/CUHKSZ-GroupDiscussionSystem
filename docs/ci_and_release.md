# CI & release notes

## GitHub Actions (`.github/workflows/ci.yml`)

On push/PR to `main`/`master`:

1. Install `pip install -e ".[dev]"`.
2. **`pytest`** — full suite; uses mock provider and local fixtures.
3. **`python main.py validate-env`** — structured environment checks with repo paths.
4. **`python main.py run-smoke`** — end-to-end session/turn/auto/feedback on `dev_snapshot_v2` + `tc-campus-ai`.
5. **`python main.py run-evals`** — `tests/fixtures/evals/suites/smoke_suite.yaml` against `dev_snapshot_v2`.

No Docker build is required for CI. No external LLM or network calls are needed when `DEFAULT_PROVIDER=mock`.

## Why mock by default

- Deterministic tests and CI.
- No API keys in forks or PRs.
- OpenAI-compatible mode remains opt-in via env and provider name.

## Local “CI-like” run

```bash
pip install -e ".[dev]"
python -m pytest
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
python main.py run-evals \
  --suite-file tests/fixtures/evals/suites/smoke_suite.yaml \
  --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 \
  --profile-id default \
  --output-dir storage/eval_reports/local_smoke
```
