"""Filesystem persistence for speech analysis JSON."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from app.audio.analysis.schemas.packet import SpeechAnalysisPacket
from app.audio.analysis.schemas.report import SessionSpeechReport


class SpeechReportStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def session_dir(self, session_id: str) -> Path:
        return self._root / session_id

    def save_turn_packet(self, session_id: str, turn_id: str, packet: SpeechAnalysisPacket) -> Path:
        d = self.session_dir(session_id)
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"turn_{turn_id}.json"
        p.write_text(packet.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return p

    def save_session_report(self, session_id: str, report: SessionSpeechReport) -> Path:
        d = self.session_dir(session_id)
        d.mkdir(parents=True, exist_ok=True)
        p = d / "session_report.json"
        p.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return p

    def load_turn_packet(self, session_id: str, turn_id: str) -> SpeechAnalysisPacket | None:
        p = self.session_dir(session_id) / f"turn_{turn_id}.json"
        if not p.is_file():
            return None
        return SpeechAnalysisPacket.model_validate(json.loads(p.read_text(encoding="utf-8")))

    def load_session_report(self, session_id: str) -> SessionSpeechReport | None:
        p = self.session_dir(session_id) / "session_report.json"
        if not p.is_file():
            return None
        return SessionSpeechReport.model_validate(json.loads(p.read_text(encoding="utf-8")))

    def list_turn_ids(self, session_id: str) -> list[str]:
        d = self.session_dir(session_id)
        if not d.is_dir():
            return []
        out: list[str] = []
        for f in sorted(d.glob("turn_*.json")):
            name = f.stem.replace("turn_", "", 1)
            out.append(name)
        return out


def new_report_id() -> str:
    return str(uuid.uuid4())
