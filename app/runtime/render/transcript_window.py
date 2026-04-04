"""Format recent transcript turns for prompts."""

from __future__ import annotations

from app.runtime.schemas.transcript import TranscriptTurn


def format_transcript_window(turns: list[TranscriptTurn], *, max_turns: int = 8) -> str:
    if not turns:
        return "(no prior turns)"
    tail = turns[-max_turns:]
    lines: list[str] = []
    for t in tail:
        who = t.speaker_role + (f"({t.speaker_name})" if t.speaker_name else "")
        lines.append(f"- [{who}] {t.text.strip()}")
    return "\n".join(lines)
