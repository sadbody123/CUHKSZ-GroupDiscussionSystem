"""Streamlit / UI configuration."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field


class UIConfig(BaseModel):
    api_base_url: str = Field(default_factory=lambda: os.environ.get("UI_API_BASE_URL", "http://127.0.0.1:8000"))


def get_ui_config() -> UIConfig:
    return UIConfig()
