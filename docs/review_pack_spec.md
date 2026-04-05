# Review pack specification

A **ReviewPack** is a JSON-serialized aggregate with:

- `review_pack_id`, `session_id`, `status` (`pending` … `closed`)
- `included_artifacts`: session summary, coach_report snapshot, transcript turns (truncated), optional mode/group/speech report dicts
- `ai_summary`: strengths/risks highlights, rubric dimensions for the workspace
- `proxy_limitations`: disclaimers for speech/learner/group proxy metrics

Audio bytes are **not** embedded; only references (e.g. speech report path key) are stored.
