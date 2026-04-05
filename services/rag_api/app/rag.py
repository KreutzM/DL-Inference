from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from pathlib import Path
from typing import Any, Protocol
import json
import math
import re

import httpx

from .config import (
    ChunkingConfig,
    CollectionConfig,
    EmbeddingsConfig,
    KnowledgeBaseConfig,
    RetrievalConfig,
    repo_root,
    VectorStoreConfig,
)

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9À-ÿ]+")


@dataclass(frozen=True)
class KnowledgeChunk:
    source_path: str
    document_id: str
    chunk_id: str
    title: str | None
    text: str
    metadata: dict[str, Any]


class VectorStoreClient(Protocol):
    def ensure_collection(self, collection: CollectionConfig) -> None: ...

    def upsert(self, collection_name: str, records: list[dict[str, Any]]) -> None: ...

    def search(self, collection_name: str, vector: list[float], limit: int) -> list[dict[str, Any]]: ...


class QdrantVectorStoreClient:
    def __init__(self, config: VectorStoreConfig) -> None:
        self.config = config

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["api-key"] = self.config.api_key
        return headers

    def _request(self, method: str, path: str, json_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            response = client.request(
                method,
                f"{self.config.url}{path}",
                headers=self._headers(),
                json=json_payload,
            )
            response.raise_for_status()
            return response.json()

    def ensure_collection(self, collection: CollectionConfig) -> None:
        response = httpx.get(
            f"{self.config.url}/collections/{collection.name}",
            headers=self._headers(),
            timeout=self.config.timeout_seconds,
        )
        if response.status_code == 200:
            return
        if response.status_code != 404:
            response.raise_for_status()
        payload = {"vectors": {"size": collection.vector_size, "distance": collection.distance}}
        self._request("PUT", f"/collections/{collection.name}", payload)

    def upsert(self, collection_name: str, records: list[dict[str, Any]]) -> None:
        points = [
            {
                "id": record["point_id"],
                "vector": record["embedding"],
                "payload": {key: value for key, value in record.items() if key not in {"point_id", "embedding"}},
            }
            for record in records
        ]
        self._request("PUT", f"/collections/{collection_name}/points?wait=true", {"points": points})

    def search(self, collection_name: str, vector: list[float], limit: int) -> list[dict[str, Any]]:
        payload = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
            "with_vectors": False,
        }
        response = self._request("POST", f"/collections/{collection_name}/points/search", payload)
        return response.get("result", []) if isinstance(response, dict) else []


def build_vector_store_client(config: VectorStoreConfig) -> VectorStoreClient:
    if config.backend != "qdrant":
        raise ValueError(f"Unsupported vector store backend for MVP: {config.backend}")
    return QdrantVectorStoreClient(config)


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def chunk_text(text: str, target_tokens: int, overlap_tokens: int) -> list[str]:
    tokens = tokenize(text)
    if not tokens:
        return []
    if len(tokens) <= target_tokens:
        return [" ".join(tokens)]

    step = max(1, target_tokens - overlap_tokens)
    chunks: list[str] = []
    for start in range(0, len(tokens), step):
        chunk_tokens = tokens[start : start + target_tokens]
        if not chunk_tokens:
            break
        chunks.append(" ".join(chunk_tokens))
        if start + target_tokens >= len(tokens):
            break
    return chunks


def embed_text(text: str, dimensions: int, normalize: bool) -> list[float]:
    vector = [0.0] * dimensions
    tokens = tokenize(text)
    for token in tokens:
        digest = blake2b(token.encode("utf-8"), digest_size=16).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        weight = 1.0 + (len(token) / 10.0)
        vector[index] += weight

    if normalize:
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude:
            vector = [value / magnitude for value in vector]
    return vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _collection_name(kb: KnowledgeBaseConfig, vector_store: VectorStoreConfig) -> str:
    return vector_store.collection_name_template.format(knowledge_base=kb.collection)


def _portable_repo_path(path: Path) -> str:
    root = repo_root()
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _point_id(kb: KnowledgeBaseConfig, chunk: KnowledgeChunk) -> int:
    digest = blake2b(f"{kb.name}:{chunk.chunk_id}".encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") & ((1 << 63) - 1)


def _load_source_chunks(kb: KnowledgeBaseConfig, chunking: ChunkingConfig) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for pattern in kb.source_globs:
        for path in sorted(kb.source_root.glob(pattern)):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            chunked_text = chunk_text(text, chunking.target_tokens, chunking.overlap_tokens)
            if not chunked_text:
                continue
            document_id = path.relative_to(kb.source_root).as_posix()
            for index, chunk in enumerate(chunked_text):
                chunks.append(
                    KnowledgeChunk(
                        source_path=_portable_repo_path(path),
                        document_id=document_id,
                        chunk_id=f"{document_id}#chunk-{index + 1}",
                        title=path.stem.replace("-", " ").replace("_", " ").title(),
                        text=chunk,
                        metadata={
                            "source_root": _portable_repo_path(kb.source_root),
                            "relative_path": document_id,
                            "chunk_index": index,
                        },
                    )
                )
    return chunks


def _ensure_embedding_alignment(embeddings: EmbeddingsConfig, collection: CollectionConfig) -> None:
    if embeddings.dimensions != collection.vector_size:
        raise ValueError(
            "Embedding dimensions and collection vector size must match for the MVP: "
            f"{embeddings.dimensions} != {collection.vector_size}"
        )


def ingest_knowledge_base(
    kb: KnowledgeBaseConfig,
    embeddings: EmbeddingsConfig,
    chunking: ChunkingConfig,
    vector_store: VectorStoreConfig,
    collection: CollectionConfig,
) -> dict[str, Any]:
    _ensure_embedding_alignment(embeddings, collection)
    chunks = _load_source_chunks(kb, chunking)
    if not chunks:
        raise FileNotFoundError(f"No source documents found for MVP knowledge base: {kb.name}")
    store = build_vector_store_client(vector_store)
    collection_name = _collection_name(kb, vector_store)
    store.ensure_collection(collection)

    records: list[dict[str, Any]] = []
    for chunk in chunks:
        records.append(
            {
                "point_id": _point_id(kb, chunk),
                "source_id": f"{kb.name}:{chunk.chunk_id}",
                "knowledge_base": kb.name,
                "collection": kb.collection,
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "source": chunk.source_path,
                "title": chunk.title,
                "text": chunk.text,
                "embedding": embed_text(chunk.text, embeddings.dimensions, embeddings.normalize),
                "metadata": chunk.metadata,
            }
        )

    store.upsert(collection_name, records)
    return {
        "status": "ok",
        "knowledge_base": kb.name,
        "assistant": kb.assistant,
        "collection": collection_name,
        "documents_ingested": len({item.document_id for item in chunks}),
        "chunks_indexed": len(records),
        "vector_store_path": f"{vector_store.url}/collections/{collection_name}",
        "meta": {
            "embeddings_provider": embeddings.provider,
            "embeddings_model": embeddings.model,
            "dimensions": embeddings.dimensions,
            "normalize": embeddings.normalize,
        },
    }


def retrieve_knowledge(
    query: str,
    kb: KnowledgeBaseConfig,
    assistant_name: str,
    embeddings: EmbeddingsConfig,
    retrieval: RetrievalConfig,
    vector_store: VectorStoreConfig,
    collection: CollectionConfig,
    top_k: int | None = None,
) -> dict[str, Any]:
    _ensure_embedding_alignment(embeddings, collection)
    store = build_vector_store_client(vector_store)
    collection_name = _collection_name(kb, vector_store)
    query_embedding = embed_text(query, embeddings.dimensions, embeddings.normalize)
    limit = max(1, top_k or retrieval.top_k)
    selected = store.search(collection_name, query_embedding, limit)

    sources: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    for index, item in enumerate(selected, start=1):
        payload = item.get("payload", {}) if isinstance(item, dict) else {}
        source_id = str(payload.get("source_id", f"{kb.name}:chunk-{index}"))
        score = float(item.get("score", 0.0))
        source = {
            "source_id": source_id,
            "document_id": str(payload.get("document_id", "")),
            "chunk_id": str(payload.get("chunk_id", "")),
            "score": score,
            "source": str(payload.get("source", "")),
            "title": payload.get("title"),
            "text": str(payload.get("text", "")),
            "metadata": dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), dict) else {},
        }
        sources.append(source)
        citations.append(
            {
                "citation_id": f"cite-{index}",
                "source_id": source_id,
                "document_id": source["document_id"],
                "chunk_id": source["chunk_id"],
                "source": source["source"],
                "score": score,
            }
        )

    return {
        "status": "ok",
        "assistant": assistant_name,
        "knowledge_base": kb.name,
        "query": query,
        "top_k": limit,
        "sources": sources,
        "citations": citations,
        "meta": {
            "collection": collection_name,
            "returned_chunks": len(sources),
            "embeddings_provider": embeddings.provider,
            "embeddings_model": embeddings.model,
            "retrieval_policy": {
                "top_k": retrieval.top_k,
                "use_hybrid": retrieval.use_hybrid,
            },
        },
    }
