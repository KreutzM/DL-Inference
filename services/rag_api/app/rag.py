from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from pathlib import Path
from typing import Any
import json
import math
import re

from .config import (
    ChunkingConfig,
    EmbeddingsConfig,
    KnowledgeBaseConfig,
    RetrievalConfig,
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


def _vector_store_path(kb: KnowledgeBaseConfig, vector_store: VectorStoreConfig) -> Path:
    return vector_store.root / vector_store.filename_template.format(knowledge_base=kb.name)


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
                        source_path=path.as_posix(),
                        document_id=document_id,
                        chunk_id=f"{document_id}#chunk-{index + 1}",
                        title=path.stem.replace("-", " ").replace("_", " ").title(),
                        text=chunk,
                        metadata={
                            "source_root": kb.source_root.as_posix(),
                            "relative_path": document_id,
                            "chunk_index": index,
                        },
                    )
                )
    return chunks


def _write_store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_store(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Vector store not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Vector store payload must be a mapping: {path}")
    return data


def ingest_knowledge_base(
    kb: KnowledgeBaseConfig,
    embeddings: EmbeddingsConfig,
    chunking: ChunkingConfig,
    vector_store: VectorStoreConfig,
) -> dict[str, Any]:
    chunks = _load_source_chunks(kb, chunking)
    store_path = _vector_store_path(kb, vector_store)
    records: list[dict[str, Any]] = []

    for chunk in chunks:
        records.append(
            {
                "source_id": f"{kb.name}:{chunk.chunk_id}",
                "knowledge_base": kb.name,
                "collection": kb.collection,
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "source_path": chunk.source_path,
                "title": chunk.title,
                "text": chunk.text,
                "embedding": embed_text(chunk.text, embeddings.dimensions, embeddings.normalize),
                "metadata": chunk.metadata,
            }
        )

    payload = {
        "knowledge_base": kb.name,
        "collection": kb.collection,
        "assistant": kb.assistant,
        "vector_store": {
            "backend": vector_store.backend,
            "path": store_path.as_posix(),
        },
        "embeddings": {
            "provider": embeddings.provider,
            "model": embeddings.model,
            "dimensions": embeddings.dimensions,
            "normalize": embeddings.normalize,
        },
        "chunking": {
            "target_tokens": chunking.target_tokens,
            "overlap_tokens": chunking.overlap_tokens,
        },
        "documents_ingested": len({item.document_id for item in chunks}),
        "chunks_indexed": len(records),
        "records": records,
    }
    _write_store(store_path, payload)
    return {
        "status": "ok",
        "knowledge_base": kb.name,
        "assistant": kb.assistant,
        "collection": kb.collection,
        "documents_ingested": payload["documents_ingested"],
        "chunks_indexed": payload["chunks_indexed"],
        "vector_store_path": store_path.as_posix(),
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
    top_k: int | None = None,
) -> dict[str, Any]:
    store_path = _vector_store_path(kb, vector_store)
    store = _read_store(store_path)
    records = store.get("records", [])
    if not isinstance(records, list):
        raise ValueError(f"Vector store payload is invalid: {store_path}")

    query_embedding = embed_text(query, embeddings.dimensions, embeddings.normalize)
    scored_records: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        embedding = record.get("embedding", [])
        if not isinstance(embedding, list):
            continue
        scored_record = dict(record)
        scored_record["score"] = cosine_similarity(query_embedding, [float(value) for value in embedding])
        scored_records.append(scored_record)

    limit = max(1, top_k or retrieval.top_k)
    scored_records.sort(key=lambda item: item["score"], reverse=True)
    selected = scored_records[:limit]

    sources: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    for index, item in enumerate(selected, start=1):
        source_id = str(item.get("source_id", f"{kb.name}:{item.get('chunk_id', index)}"))
        source = {
            "source_id": source_id,
            "document_id": str(item.get("document_id", "")),
            "chunk_id": str(item.get("chunk_id", "")),
            "score": float(item.get("score", 0.0)),
            "title": item.get("title"),
            "source_path": item.get("source_path"),
            "text": str(item.get("text", "")),
            "metadata": dict(item.get("metadata", {})) if isinstance(item.get("metadata"), dict) else {},
        }
        sources.append(source)
        citations.append(
            {
                "citation_id": f"cite-{index}",
                "source_id": source_id,
                "document_id": source["document_id"],
                "chunk_id": source["chunk_id"],
                "source_path": source["source_path"],
                "score": source["score"],
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
            "vector_store_path": store_path.as_posix(),
            "stored_chunks": len(records),
            "returned_chunks": len(sources),
            "embeddings_provider": embeddings.provider,
            "embeddings_model": embeddings.model,
            "retrieval_policy": {
                "top_k": retrieval.top_k,
                "use_hybrid": retrieval.use_hybrid,
            },
        },
    }
