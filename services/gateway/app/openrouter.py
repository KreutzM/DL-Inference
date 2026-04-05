from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class OpenRouterSettings:
    api_key: str
    base_url: str


def load_openrouter_settings() -> OpenRouterSettings:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required for the MVP gateway path")
    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    return OpenRouterSettings(api_key=api_key, base_url=base_url)


class OpenRouterClient:
    def __init__(self, settings: OpenRouterSettings) -> None:
        self.settings = settings

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
