"""Assignment filesystem persistence."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.curriculum.schemas.assignment import AssignmentSpec
from app.curriculum.schemas.delivery import DeliverySummary
from app.curriculum.schemas.report import AssignmentReport
from app.curriculum.schemas.attempt import AssignmentAttempt

_SAFE = re.compile(r"^[\w.\-]+$")


class AssignmentStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self._global_index = self._root / "index.json"

    def _adir(self, assignment_id: str) -> Path:
        if not _SAFE.match(assignment_id):
            raise ValueError("invalid assignment_id")
        return self._root / assignment_id

    def create_assignment(self, spec: AssignmentSpec) -> Path:
        d = self._adir(spec.assignment_id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "spec.json").write_text(json.dumps(spec.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._touch_index(spec)
        return d

    def _touch_index(self, spec: AssignmentSpec) -> None:
        data: dict = {}
        if self._global_index.is_file():
            try:
                data = json.loads(self._global_index.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
        assigns = data.setdefault("assignments", {})
        assigns[spec.assignment_id] = {
            "title": spec.title,
            "pack_id": spec.pack_id,
            "status": spec.status,
            "learner_ids": spec.learner_ids,
        }
        for lid in spec.learner_ids:
            lm = data.setdefault("learner_map", {})
            lm.setdefault(lid, []).append(spec.assignment_id)
        self._global_index.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def load_assignment(self, assignment_id: str) -> AssignmentSpec | None:
        p = self._adir(assignment_id) / "spec.json"
        if not p.is_file():
            return None
        return AssignmentSpec.model_validate_json(p.read_text(encoding="utf-8"))

    def save_assignment(self, spec: AssignmentSpec) -> None:
        d = self._adir(spec.assignment_id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "spec.json").write_text(json.dumps(spec.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._touch_index(spec)

    def list_assignments(self) -> list[AssignmentSpec]:
        out: list[AssignmentSpec] = []
        if not self._root.is_dir():
            return out
        for child in sorted(self._root.iterdir()):
            if not child.is_dir():
                continue
            spec = self.load_assignment(child.name)
            if spec:
                out.append(spec)
        return sorted(out, key=lambda x: x.created_at, reverse=True)

    def append_attempt(self, assignment_id: str, attempt: AssignmentAttempt) -> Path:
        d = self._adir(assignment_id)
        p = d / "attempts.jsonl"
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(attempt.model_dump(), ensure_ascii=False) + "\n")
        return p

    def save_delivery_summary(self, assignment_id: str, summary: DeliverySummary) -> Path:
        d = self._adir(assignment_id)
        p = d / "delivery_summary.json"
        p.write_text(json.dumps(summary.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_delivery_summary(self, assignment_id: str) -> DeliverySummary | None:
        p = self._adir(assignment_id) / "delivery_summary.json"
        if not p.is_file():
            return None
        return DeliverySummary.model_validate_json(p.read_text(encoding="utf-8"))

    def save_report(self, assignment_id: str, report: AssignmentReport) -> Path:
        d = self._adir(assignment_id)
        p = d / "report.json"
        p.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_report(self, assignment_id: str) -> AssignmentReport | None:
        p = self._adir(assignment_id) / "report.json"
        if not p.is_file():
            return None
        return AssignmentReport.model_validate_json(p.read_text(encoding="utf-8"))

    def list_attempts(self, assignment_id: str) -> list[AssignmentAttempt]:
        p = self._adir(assignment_id) / "attempts.jsonl"
        if not p.is_file():
            return []
        out: list[AssignmentAttempt] = []
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(AssignmentAttempt.model_validate_json(line))
            except Exception:
                continue
        return out
