"""OpenAI-compatible chat completions HTTP client (stdlib only, optional)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from app.runtime.llm.base import BaseLLMProvider
from app.runtime.schemas.llm import GenerationRequest, GenerationResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    name = "openai_compatible"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.default_model = default_model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set; use provider=mock for offline runs.")
        model = request.model or self.default_model
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature if request.temperature is not None else 0.7,
        }
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible HTTP error: {e.code} {err}") from e
        text = ""
        try:
            text = raw["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            text = json.dumps(raw)[:2000]
        return GenerationResponse(
            provider_name=self.name,
            model=model,
            text=text,
            raw=raw,
            metadata={},
        )
