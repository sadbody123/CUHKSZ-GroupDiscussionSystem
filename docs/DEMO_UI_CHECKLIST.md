# Manual UI demo checklist (repeatable)

This is the **recommended** way to demo the Streamlit UI against a local API. It mirrors `tests/test_api_ui_core_flow.py` (mock provider, `dev_snapshot_v2`).

## Prerequisites

- Python 3.11+, `pip install -e ".[dev]"` (API + UI + tests require the `dev` extra).
- Prepare the demo snapshot once: `python main.py bootstrap-dev-snapshot` (or `make bootstrap-dev-snapshot`).
- Copy `.env.example` to `.env` only if you need non-default paths.

## Steps

1. **Terminal A — API**  
   `python main.py run-api`  
   Default: `http://127.0.0.1:8000`

2. **Terminal B — UI**  
   `python main.py run-ui --api-base-url http://127.0.0.1:8000`  
   Or set `UI_API_BASE_URL` to the same URL.

3. **In the UI**  
   - Confirm sidebar shows API health (version + default provider **mock**).  
   - Select snapshot **`dev_snapshot_v2`** (or the snapshot you built).  
   - Pick a **topic** from the list.  
   - **Create session** (runtime profile **default** is fine).

4. **Discussion**  
   - Type a **user turn** and submit.  
   - Run **next turn** (agent reply).  
   - Optionally run additional turns or auto-run if exposed in controls.

5. **Feedback**  
   - Open the feedback panel and **generate feedback**.  
   - Expect coach-style text; with **mock** LLM, wording is deterministic/templated.

## Optional / experimental surfaces

Learner dashboards, review workspace, curriculum assignments, authoring studio, release/stability panels, and audio upload are **optional**. Prefer **`provider_name=mock`** and skip cloud ASR/TTS unless you explicitly configure keys. Those outputs are **advisory / training support only** — not official assessment or certification.

## If something fails

- Run `python main.py validate-env` and fix any **errors** (writable dirs, default profile).  
- Re-run `python main.py bootstrap-dev-snapshot` if `/topics` or snapshot listing is empty.
