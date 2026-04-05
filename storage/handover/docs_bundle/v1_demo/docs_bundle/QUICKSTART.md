# Quickstart (local)

1. Create/activate a Python 3.11+ environment and **`pip install -e ".[dev]"`** (required for API, UI, and pytest).
2. Build the demo snapshot once: **`python main.py bootstrap-dev-snapshot`** (or `make bootstrap-dev-snapshot`).
3. Validate environment: `python main.py validate-env`
4. Smoke the core loop (optional but recommended):  
   `python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default`
5. Start API: `python main.py run-api`
6. Start UI (second terminal): `python main.py run-ui` — follow `docs/DEMO_UI_CHECKLIST.md` for a repeatable walkthrough.
7. Optional release checks (advisory only): `python main.py audit-release-readiness --profile-id v1_demo`
8. Optional delivery verification (advisory only): `python main.py verify-delivery --profile-id v1_demo`

**Default:** `mock` LLM and mock audio providers (offline). Cloud LLM/ASR/TTS are optional and not CI-guaranteed — see `docs/providers_truth_table.md` and `docs/llm_integration.md`.
