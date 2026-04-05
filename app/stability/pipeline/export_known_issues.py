"""Export known limitations / issues as Markdown."""

from __future__ import annotations

from pathlib import Path

from app.stability.engines.known_limitations import accepted_limitation_lines
from app.stability.schemas.issue import IssueRecord


def export_known_limitations_md(
    rows: list[IssueRecord],
    *,
    profile_id: str,
    output_file: Path,
) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Known limitations (profile `{profile_id}`)",
        "",
        "## Accepted limitations",
        "",
        *(accepted_limitation_lines(rows) or ["- None recorded."]),
        "",
        "## Open / mitigated (summary)",
        "",
    ]
    for r in rows:
        if r.status == "accepted_limitation":
            continue
        lines.append(f"- **{r.issue_id}** [{r.severity}] {r.title} — {r.status}")
    lines.append("")
    output_file.write_text("\n".join(lines), encoding="utf-8")
    return output_file
