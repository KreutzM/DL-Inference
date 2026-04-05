from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ASSISTANT_CONFIG_PATH = REPO_ROOT / "services" / "assistant-config" / "assistants" / "mvp-openrouter.yaml"


@dataclass(frozen=True)
class MvpAssistant:
    name: str
    model: str
    system_prompt: str
    knowledge_base: str
    retrieval_policy: str


def load_mvp_assistant() -> MvpAssistant:
    data = yaml.safe_load(ASSISTANT_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("MVP assistant config must be a mapping")

    required = ("name", "model", "system_prompt", "knowledge_base", "retrieval_policy")
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError(f"MVP assistant config missing required fields: {', '.join(missing)}")

    return MvpAssistant(
        name=str(data["name"]),
        model=str(data["model"]),
        system_prompt=str(data["system_prompt"]),
        knowledge_base=str(data["knowledge_base"]),
        retrieval_policy=str(data["retrieval_policy"]),
    )


def load_mvp_system_prompt_text() -> str:
    assistant = load_mvp_assistant()
    system_prompt_path = REPO_ROOT / assistant.system_prompt
    if not system_prompt_path.exists():
        raise ValueError(f"MVP assistant system prompt not found: {assistant.system_prompt}")
    return system_prompt_path.read_text(encoding="utf-8")


def assistant_summary() -> dict[str, Any]:
    assistant = load_mvp_assistant()
    return {
        "id": assistant.name,
        "object": "model",
        "owned_by": "repo2",
        "metadata": {
            "assistant": assistant.name,
            "model": assistant.model,
            "knowledge_base": assistant.knowledge_base,
            "retrieval_policy": assistant.retrieval_policy,
        },
    }
