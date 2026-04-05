# Demo script (v1_demo, mock)

1. `pip install -e ".[dev]"` (if not already)
2. **`python main.py bootstrap-dev-snapshot`** — ensures `dev_snapshot_v2` exists (or skips if valid)
3. `python main.py validate-env`
4. `python main.py audit-release-readiness --profile-id v1_demo` *(advisory tooling)*
5. `python main.py run-demo-scenario --scenario-id text_core_demo --profile-id v1_demo --snapshot-id dev_snapshot_v2 --provider mock`
6. `python main.py run-api` then `python main.py run-ui` — UI steps: `docs/DEMO_UI_CHECKLIST.md`
7. Optional: `python main.py build-handover-kit --profile-id v1_demo --output-dir tmp/handover_out` *(advisory bundle)*

Handover, readiness, and stability outputs are **not** formal certification — see `KNOWN_LIMITATIONS_FINAL.md`.

