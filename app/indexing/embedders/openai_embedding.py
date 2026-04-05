"""Optional OpenAI-compatible embedding HTTP client."""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.indexing.embedders.base import BaseEmbedder
from app.indexing.schemas.embedding import EmbeddingRequest, EmbeddingResponse


class OpenAIEmbeddingProvider(BaseEmbedder):
    name = "openai"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL") or "text-embedding-3-small"
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set for OpenAIEmbeddingProvider")

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResponse:
        url = f"{self.base_url}/embeddings"
        payload: dict[str, Any] = {"model": self.model, "input": request.texts}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        rows_raw = sorted(data["data"], key=lambda x: int(x["index"]))
        rows = [list(map(float, row["embedding"])) for row in rows_raw]
        dim = len(rows[0]) if rows else 0
        return EmbeddingResponse(
            embedder_name=self.name,
            model_name=self.model,
            vectors=rows,
            dimension=dim,
            metadata={},
        )
