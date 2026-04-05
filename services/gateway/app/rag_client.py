from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import httpx


@dataclass(frozen=True)
class RagApiSettings:
    base_url: str


def load_rag_api_settings() -> RagApiSettings:
    base_url = os.environ.get("RAG_API_URL", "http://rag_api:8010").strip().rstrip("/")
    if not base_url:
        raise ValueError("RAG_API_URL is required when retrieval is enabled in the MVP gateway path")
    return RagApiSettings(base_url=base_url)


class RagApiClient:
    def __init__(self, settings: RagApiSettings) -> None:
        self.settings = settings

    def retrieve(
        self,
        *,
        query: str,
        assistant: str,
        knowledge_base: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        payload = {
            "query": query,
            "assistant": assistant,
            "knowledge_base": knowledge_base,
            "top_k": top_k,
        }
        url = f"{self.settings.base_url}/retrieve"
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("RAG API returned an invalid response")
            return data
