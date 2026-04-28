"""Lightweight reply cleanup with multi-agent quality controls."""

from __future__ import annotations

import re


def _strip_other_agent_prefixes(text: str, current_role: str | None = None, participant_names: list[str] | None = None) -> str:
    """Remove lines where the LLM starts speaking as another agent by prefixing
    with that agent's name followed by a colon.  Lines that begin with an *other*
    agent's name + colon are discarded entirely (the content belongs to that agent,
    not the current speaker).  Lines that begin with the *current* role's name + colon
    have only the prefix stripped.
    """
    names: list[str] = list(participant_names or [])
    if current_role:
        names.append(str(current_role))
    if not names:
        return text

    name_pattern = "|".join(re.escape(n.strip()) for n in names if n.strip())
    prefix_re = re.compile(rf"^({name_pattern})\s*[:：]\s*", re.IGNORECASE)

    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        m = prefix_re.match(line)
        if m:
            prefix_name = m.group(1).strip().lower()
            current_lower = (current_role or "").lower()
            if prefix_name == current_lower:
                result.append(line[m.end():])
        else:
            result.append(line)
    return "\n".join(result)


def _strip_repeated_template_markers(text: str) -> str:
    text = re.sub(r"\[REPAIR\]\s*", "", text)
    text = re.sub(r"(\[Guidance:[^\]]*\]\s*){2,}", r"\1", text)
    text = re.sub(r"Guidance:\s*Guidance:", "Guidance:", text)
    return text


def _collapse_repeated_lines(text: str) -> str:
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        if len(result) >= 2 and result[-1] == line and result[-2] == line:
            continue
        result.append(line)
    return "\n".join(result)


def postprocess_reply(
    text: str,
    *,
    max_chars: int | None = None,
    current_role: str | None = None,
    participant_names: list[str] | None = None,
) -> str:
    """Clean up an LLM-generated reply.

    Args:
        text: Raw LLM output.
        max_chars: Optional maximum character length.
        current_role: The role of the current speaker (to preserve its own prefix).
        participant_names: Other participant display names to scrub from the reply.
    """
    t = text.strip()

    t = _strip_other_agent_prefixes(t, current_role=current_role, participant_names=participant_names)
    t = _strip_repeated_template_markers(t)
    t = _collapse_repeated_lines(t)

    if max_chars is not None and len(t) > max_chars:
        t = t[:max_chars] + ("..." if max_chars > 3 else "")

    return t