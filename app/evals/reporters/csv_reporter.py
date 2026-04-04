"""CSV report."""

from __future__ import annotations

import csv
from pathlib import Path

from app.evals.schemas.report import EvalReport


def write(path: Path, report: EvalReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["case_id", "case_type", "passed", "score", "profile_id"],
            extrasaction="ignore",
        )
        w.writeheader()
        for r in report.results:
            pid = r.get("profile_id") or (r.get("metadata") or {}).get("profile_id", "")
            w.writerow(
                {
                    "case_id": r.get("case_id"),
                    "case_type": r.get("case_type"),
                    "passed": r.get("passed"),
                    "score": r.get("score"),
                    "profile_id": pid,
                }
            )
