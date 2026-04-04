# Local runbook (phase 5)

## 1. Prepare a snapshot

Build a phase-2 snapshot (example):

```bash
python main.py build-offline ^
  --input-dir tests/fixtures/datahub_exports ^
  --pedagogy-dir tests/fixtures/pedagogy ^
  --topic-card-dir tests/fixtures/topic_cards ^
  --snapshot-id dev_snapshot_v2
```

Validate:

```bash
python main.py validate-snapshot --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2
```

## 2. Start the API

```bash
pip install -e ".[dev]"
python main.py run-api --host 127.0.0.1 --port 8000
```

Check:

```bash
curl -s http://127.0.0.1:8000/health
```

Optional env:

- `SESSION_STORAGE_DIR` — where session JSON files go (default `storage/sessions`)
- `SNAPSHOT_ROOT` — snapshot parent directory (see `.env.example`)
- `DEFAULT_PROVIDER` — default `mock`

## 3. Start the Streamlit UI

```bash
python main.py run-ui --api-base-url http://127.0.0.1:8000
```

## 4. Demo flow

1. Pick snapshot **dev_snapshot_v2** and a topic.
2. Create session (provider **mock**).
3. Submit a user message → **Run next** → **Auto run** a few steps.
4. **Generate feedback** and read the coach preview.
5. (Optional) `GET /sessions/{id}/export` for full JSON.

## 5. CLI still works

Phase-4 commands (`create-session`, `submit-user-turn`, …) are unchanged; they use the same session store and runtime.
