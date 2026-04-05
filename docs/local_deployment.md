# Local deployment

## Python (recommended for development)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Optional: copy `.env.example` to `.env` and set `SNAPSHOT_ROOT`, `SESSION_STORAGE_DIR`, etc.

## API

```bash
python main.py run-api --host 127.0.0.1 --port 8000
# or
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

## Streamlit UI

```bash
set UI_API_BASE_URL=http://127.0.0.1:8000   # PowerShell: $env:UI_API_BASE_URL=...
python main.py run-ui --api-base-url http://127.0.0.1:8000
# or
streamlit run app/ui/streamlit_app.py
```

## Docker Compose

From the repository root:

```bash
docker compose -f docker/docker-compose.yml up --build
```

- API: `http://localhost:8000`
- UI: `http://localhost:8501` (defaults `UI_API_BASE_URL=http://api:8000` inside the compose network)

Mount `app/knowledge/snapshots` is configured so local snapshot folders remain visible in the API container.

## Smoke verification

```bash
python main.py validate-env
python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default
```
