from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[3]
MODELS_CONFIG = REPO_ROOT / "configs" / "inference" / "models.yaml"
MVP_MODEL_ALIAS = "mvp_openrouter_chat"


class MvpModelRoute(BaseModel):
    alias: str
    provider_model_id: str
    assistant: str
    family: str | None = None
    backend: str | None = None


def _load_raw_models() -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(MODELS_CONFIG.read_text(encoding="utf-8")) or {}
    models = data.get("models", {})
    if not isinstance(models, dict):
        raise ValueError("configs/inference/models.yaml must define a mapping under 'models'")
    return models


def list_models() -> list[dict[str, Any]]:
    raw_models = _load_raw_models()
    results: list[dict[str, Any]] = []

    for model_name, config in raw_models.items():
        if not config.get("mvp"):
            continue
        results.append(
            {
                "id": model_name,
                "object": "model",
                "owned_by": "repo2",
                "metadata": {
                    "assistant": config.get("assistant"),
                    "backend": config.get("backend"),
                    "family": config.get("family"),
                    "provider_model_id": config.get("model_id"),
                    "model_id": config.get("model_id"),
                },
            }
        )
    return results


def load_mvp_model_route() -> MvpModelRoute:
    raw_models = _load_raw_models()
    config = raw_models.get(MVP_MODEL_ALIAS)
    if not isinstance(config, dict) or not config.get("mvp"):
        raise ValueError(f"MVP model config missing for alias: {MVP_MODEL_ALIAS}")

    provider_model_id = config.get("model_id")
    assistant = config.get("assistant")
    if not provider_model_id or not assistant:
        raise ValueError("MVP model config must define 'model_id' and 'assistant'")

    return MvpModelRoute(
        alias=MVP_MODEL_ALIAS,
        provider_model_id=str(provider_model_id),
        assistant=str(assistant),
        family=str(config.get("family")) if config.get("family") else None,
        backend=str(config.get("backend")) if config.get("backend") else None,
    )


def resolve_model(model: str | None) -> str:
    available = {item["id"] for item in list_models()}
    candidate = model or MVP_MODEL_ALIAS
    if candidate not in available:
        raise ValueError(f"Unknown model: {candidate}")
    return candidate
