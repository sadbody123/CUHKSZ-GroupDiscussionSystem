# LLM integration (phase 4)

## Provider abstraction

- **`app/runtime/llm/base.py`** — `LLMProvider.generate(GenerationRequest) -> GenerationResponse`.
- **`app/runtime/llm/manager.py`** — resolves a provider by name (`mock`, `openai_compatible`, …).
- **`app/runtime/llm/config.py`** — reads optional env defaults (`LLM_PROVIDER`, `OPENAI_*`).
- **`app/runtime/schemas/llm.py`** — `LLMMessage`, `GenerationRequest`, `GenerationResponse`.

Runtime code and tests should depend on **`GenerationRequest` / `GenerationResponse`**, not on a specific vendor SDK.

## Mock provider

- **`app/runtime/llm/providers/mock_provider.py`**
- **No network.** Deterministic output for the same request (messages + metadata such as `role`).
- Different `metadata["role"]` values (`moderator`, `ally`, `opponent`, `coach`) produce distinguishable fixed text for demos and pytest.
- **Default for CLI and tests** when `--provider mock` or `provider_name=mock`.

## OpenAI-compatible provider

- **`app/runtime/llm/providers/openai_compatible.py`**
- Minimal **chat-completions**-style HTTP call (stdlib only; no required extra package).
- Reads:
  - `LLM_PROVIDER` — when set to `openai_compatible`, manager can select this provider.
  - `OPENAI_API_KEY` — required to actually call the API; if missing, instantiation/call fails with a clear error (tests do not exercise this path).
  - `OPENAI_BASE_URL` — optional base URL (OpenAI-compatible servers).
  - `OPENAI_MODEL` — optional model id.

If the key is absent or you stay on **`mock`**, the project runs fully offline.

## Why tests do not hit real APIs

- Pytest uses **`MockProvider`** only (or stubs that do not open sockets).
- Integration tests for discussion flow use **`--provider mock`** and file-backed sessions under `storage/sessions/` or a temp directory.
- No API key is required for `pytest` or for CLI demos with mock.

**Delivery expectation:** the **default, supported** path for demos and CI is **`mock`**. OpenAI-compatible and other HTTP providers are **optional**; they may return different content, latency, and failure modes than `mock`. **Do not treat cloud parity as guaranteed** without your own validation.

See also: [CLI discussion MVP](cli_discussion_mvp.md), [providers_truth_table](providers_truth_table.md).
