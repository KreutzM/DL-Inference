from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import (
    load_chunking_config,
    load_embeddings_config,
    load_knowledge_base_config,
    load_mvp_assistant_config,
    load_retrieval_config,
    load_vector_store_config,
)
from .rag import ingest_knowledge_base, retrieve_knowledge

app = FastAPI(title="Repo2 RAG API", version="0.1.0")


class IngestRequest(BaseModel):
    assistant: str | None = None
    knowledge_base: str | None = None
    force: bool = False


class IngestResponse(BaseModel):
    status: str
    assistant: str
    knowledge_base: str
    collection: str
    documents_ingested: int
    chunks_indexed: int
    vector_store_path: str
    meta: dict[str, Any] = Field(default_factory=dict)


class RetrieveRequest(BaseModel):
    query: str
    assistant: str | None = None
    knowledge_base: str | None = None
    top_k: int = 5


class RetrievedSource(BaseModel):
    source_id: str
    document_id: str
    chunk_id: str
    score: float
    title: str | None = None
    source_path: str | None = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CitationItem(BaseModel):
    citation_id: str
    source_id: str
    document_id: str
    chunk_id: str
    source_path: str | None = None
    score: float


class RetrieveResponse(BaseModel):
    status: str
    assistant: str
    knowledge_base: str
    query: str
    top_k: int
    sources: list[RetrievedSource] = Field(default_factory=list)
    citations: list[CitationItem] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


def _resolve_active_knowledge_base(requested: str | None) -> tuple[str, str]:
    assistant = load_mvp_assistant_config()
    knowledge_base = load_knowledge_base_config(requested)
    if knowledge_base.assistant != assistant.name:
        raise HTTPException(
            status_code=400,
            detail=(
                "Knowledge base config does not match the MVP assistant: "
                f"{knowledge_base.assistant} != {assistant.name}"
            ),
        )
    return assistant.name, knowledge_base.name


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag_api"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    assistant_name, knowledge_base_name = _resolve_active_knowledge_base(request.knowledge_base)
    if request.assistant and request.assistant != assistant_name:
        raise HTTPException(status_code=400, detail=f"Unknown MVP assistant: {request.assistant}")

    kb = load_knowledge_base_config(knowledge_base_name)
    embeddings = load_embeddings_config()
    chunking = load_chunking_config()
    vector_store = load_vector_store_config()

    payload = ingest_knowledge_base(kb, embeddings, chunking, vector_store)
    if request.force:
        payload["meta"]["force"] = True
    return IngestResponse(**payload)


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    assistant_name, knowledge_base_name = _resolve_active_knowledge_base(request.knowledge_base)
    if request.assistant and request.assistant != assistant_name:
        raise HTTPException(status_code=400, detail=f"Unknown MVP assistant: {request.assistant}")

    kb = load_knowledge_base_config(knowledge_base_name)
    embeddings = load_embeddings_config()
    retrieval = load_retrieval_config()
    vector_store = load_vector_store_config()

    try:
        payload = retrieve_knowledge(
            query=request.query,
            kb=kb,
            assistant_name=assistant_name,
            embeddings=embeddings,
            retrieval=retrieval,
            vector_store=vector_store,
            top_k=request.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"MVP knowledge base has not been ingested yet: {knowledge_base_name}",
        ) from exc

    return RetrieveResponse(
        status=payload["status"],
        assistant=payload["assistant"],
        knowledge_base=payload["knowledge_base"],
        query=payload["query"],
        top_k=payload["top_k"],
        sources=[RetrievedSource(**item) for item in payload["sources"]],
        citations=[CitationItem(**item) for item in payload["citations"]],
        meta=payload["meta"],
    )
