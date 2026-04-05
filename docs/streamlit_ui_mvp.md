# Streamlit UI MVP (phase 5)

## Layout

Single-page app: **`app/ui/streamlit_app.py`**.

- **Left column:** choose snapshot → topic → stance/provider → **Create session**.
- **Right column:** transcript, **Submit / Run next / Auto run / Generate feedback**, coach text preview when present.
- **Sidebar:** **System** panel (`/health` + `/system/info`), **Debug** (API base URL, app version, snapshot/session ids, session summary). If the API is unreachable, the app shows a clear error and skips snapshot/session actions until the API is available.

## Data path

**Streamlit → `DiscussionApiClient` (httpx) → FastAPI → application services → runtime.**

Configure the API base URL with:

- Environment variable **`UI_API_BASE_URL`** (default `http://127.0.0.1:8000`), or
- `python main.py run-ui --api-base-url http://127.0.0.1:8000`

## Running

1. Start API: `python main.py run-api --host 127.0.0.1 --port 8000`
2. Start UI: `python main.py run-ui --api-base-url http://127.0.0.1:8000`
3. Open the URL Streamlit prints (usually `http://localhost:8501`).

Alternative:

```bash
streamlit run app/ui/streamlit_app.py
```

Ensure `UI_API_BASE_URL` is set if the API is not on localhost:8000.

## Components

Under **`app/ui/components/`**: snapshot/topic selectors, session creator, transcript, controls, feedback/debug panels — thin wrappers over the API client.
