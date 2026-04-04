# Coach report (phase 4)

## FeedbackPacket vs CoachReport

- **`FeedbackPacket`** (phase 3, `app/runtime/evaluation/`) — structured output from the transcript **analyzer**: rubric-oriented signals, strengths/risks-style fields where implemented, and metadata for downstream use.
- **`CoachReport`** (phase 4, `app/runtime/schemas/coach_report.py`) — session-level **natural language** coaching plus structured slots (`strengths`, `risks`, `suggested_next_actions`, etc.) and **`metadata`** for anything that should stay machine-readable.

Typical flow:

1. Session reaches **feedback** phase (or `generate-feedback` forces this path).
2. **Analyzer** builds **`FeedbackPacket`** from transcript + snapshot context.
3. **Role router** can pull extra **pedagogy** (rubrics, coaching tips) for the coach role.
4. **Coach agent** (`app/runtime/agents/coach_agent.py`) renders **`coach.md`**, passes the feedback packet (serialized) into the prompt, and calls the **LLM provider** (mock in tests).
5. Result is stored on the session as **`coach_report`** and can be exported via **`export-session`**.

## Rubric, coaching tips, and signals

- Rubric and coaching-tip rows come from the **pedagogy** repository in the loaded snapshot.
- Transcript-derived **signals** from the analyzer are fed into the coach prompt (and router) so feedback is anchored to observed behavior, not only generic advice.

## Testing

Tests use **`MockProvider`** only: no API keys, no network. See **`tests/test_generate_feedback.py`**.
