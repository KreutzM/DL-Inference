from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Repo2 RAG API", version="0.1.0")
REPO_ROOT = Path(__file__).resolve().parents[3]
EMBEDDINGS_CONFIG = REPO_ROOT / "configs" / "rag" / "embeddings.yaml"


class RetrieveRequest(BaseModel):
    query: str
    assistant: str | None = None
    knowledge_base: str | None = None
    top_k: int = 5


class RetrievalItem(BaseModel):
    document_id: str
    chunk_id: str
    score: float
    text: str
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrieveResponse(BaseModel):
    results: list[RetrievalItem] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


def _load_embeddings_config() -> dict[str, Any]:
    data = yaml.safe_load(EMBEDDINGS_CONFIG.read_text(encoding="utf-8")) or {}
    return data.get("embeddings", {}) if isinstance(data, dict) else {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag_api"}


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    embeddings = _load_embeddings_config()
    meta = {
        "query": request.query,
        "assistant": request.assistant,
        "knowledge_base": request.knowledge_base,
        "top_k": request.top_k,
        "status": "placeholder",
        "embeddings_provider": embeddings.get("provider"),
        "embeddings_model": embeddings.get("model"),
    }
    return RetrieveResponse(results=[], meta=meta)
