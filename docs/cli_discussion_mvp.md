# CLI text discussion MVP (phase 4)

Phase 4 adds a **file-backed session** and **multi-turn discussion** commands on top of phase-3 snapshot commands (`list-topics`, `show-topic`, `retrieve-context`, `plan-turn`, `analyze-transcript`).

## Prerequisites

- Build or use a **phase-2 snapshot** (e.g. `dev_snapshot_v2` with `manifest.json` under `app/knowledge/snapshots/dev_snapshot_v2`).
- Topic ids must exist in that snapshot (e.g. `tc-campus-ai` from fixtures build). Replace `--topic-id` below with a real id from `list-topics`.

## Session storage

- Default: **`storage/sessions/<session_id>.json`** (gitignored `*.json`; directory tracked via `.gitkeep`).
- Override root: **`--storage-root <path>`** on commands that touch the session store.

## Commands

### create-session

Creates a session, binds `topic_id`, `user_stance`, snapshot path, and provider (`mock` recommended for offline use).

```bash
python main.py create-session ^
  --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 ^
  --topic-id tc-campus-ai ^
  --user-stance for ^
  --provider mock
```

### session-status

```bash
python main.py session-status --session-id <session_id>
```

Shows phase, turn count, recent transcript snippet, and whether another `run-next-turn` is meaningful.

### submit-user-turn

```bash
python main.py submit-user-turn ^
  --session-id <session_id> ^
  --text "Your message here."
```

### run-next-turn

Runs the orchestrator + agent for the **next non-user** role (moderator / ally / opponent depending on state machine). Uses the selected LLM provider (mock by default).

```bash
python main.py run-next-turn --session-id <session_id>
```

If the state machine says the next speaker is **user**, the CLI reports that it is the user’s turn (no model call).

### auto-run-discussion

Advances up to **`--max-steps`** automated steps (with optional stub user lines for demo). Useful with **mock** provider.

```bash
python main.py auto-run-discussion --session-id <session_id> --max-steps 4
```

### generate-feedback

Moves the session into the feedback path, runs the transcript **analyzer** → **`FeedbackPacket`**, then the **coach agent** → **`CoachReport`**, and persists the report on the session.

```bash
python main.py generate-feedback --session-id <session_id>
```

### export-session

```bash
python main.py export-session --session-id <session_id> --output-file tmp/session_export.json
```

## See also

- [LLM integration](llm_integration.md) — mock vs OpenAI-compatible env vars.
- [Coach report](coach_report.md) — feedback packet vs natural-language coach output.
