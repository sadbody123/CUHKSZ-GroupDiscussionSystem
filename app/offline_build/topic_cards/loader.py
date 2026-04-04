"""Load topic cards from YAML / JSON files in a directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.offline_build.topic_cards.validators import dict_to_topic_card
from app.schemas.topic_card import TopicCard


def _load_yaml(path: Path) -> Any:
    import yaml  # type: ignore[import-untyped]

    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text)


def _iter_card_dicts(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        if "topics" in data and isinstance(data["topics"], list):
            return [x for x in data["topics"] if isinstance(x, dict)]
        if "cards" in data and isinstance(data["cards"], list):
            return [x for x in data["cards"] if isinstance(x, dict)]
        return [data]
    return []


def load_topic_card_directory(topic_dir: Path | None) -> tuple[list[TopicCard], int]:
    """
    Load *.yaml, *.yml, *.json from topic_dir.

    Returns (cards, files_read).
    """
    if topic_dir is None or not topic_dir.is_dir():
        return [], 0
    cards: list[TopicCard] = []
    files_read = 0
    for p in sorted(topic_dir.iterdir()):
        if not p.is_file():
            continue
        suf = p.suffix.lower()
        if suf not in (".yaml", ".yml", ".json"):
            continue
        files_read += 1
        try:
            if suf == ".json":
                data = json.loads(p.read_text(encoding="utf-8"))
            else:
                data = _load_yaml(p)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        except Exception:
            continue
        for d in _iter_card_dicts(data):
            tc = dict_to_topic_card(d)
            if tc:
                m = dict(tc.metadata)
                m.setdefault("source_file", p.name)
                tc = tc.model_copy(update={"metadata": m})
                cards.append(tc)
    return cards, files_read
