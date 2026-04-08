# MCP / privacy notes for this repo

This project’s `.cursor/mcp.json` is intentionally **minimal and local-first**.

## What is configured

- **`project-code`** (`@modelcontextprotocol/server-filesystem`) only allows **`app/`**, **`docs/`**, and **`tests/`**.
  - **Not included:** repository root (so e.g. `.env` at the root is **not** exposed via this MCP server), **`storage/`** (runtime JSON / local reports), and other top-level folders.
  - **Trade-off:** Root files such as `main.py` and `pyproject.toml` are **not** inside those three folders. Edit them via the editor as usual, or temporarily add another allowed directory in `mcp.json` if you accept the wider blast radius.

## What is not enabled by default

- **`web-fetch` / HTTP fetch MCP** is **off by default**. Fetch tools can request arbitrary URLs and are a common source of accidental data exposure (tokens in URLs, internal endpoints, etc.). If you need it, add it back locally and only enable it when you understand the risk.

## Tokens and secrets

- **Never** commit API keys, cookies, or personal tokens into `mcp.json` or the repo.
- Prefer **user-level** Cursor MCP config or environment variables (not committed) for any server that needs credentials.

## Filesystem MCP is still powerful

Even with a narrow root, the agent can **read and write** under `app/`, `docs/`, and `tests/` when the tool is used. Review changes like you would a human contributor’s patch.

## `.cursorignore`

Patterns listed there reduce how often **local/generated** paths appear in AI context. They do **not** replace filesystem permissions or good secret hygiene.
