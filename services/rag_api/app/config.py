from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os

import yaml

REPO_ROOT_ENV = "DL_INFERENCE_REPO_ROOT"


def repo_root() -> Path:
    override = os.environ.get(REPO_ROOT_ENV, "").strip()
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[3]


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping: {path}")
    return data


def _resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (repo_root() / path).resolve()


@dataclass(frozen=True)
class MvpAssistantConfig:
    name: str
    model: str
    system_prompt: str
    knowledge_base: str
    retrieval_policy: str


@dataclass(frozen=True)
class KnowledgeBaseConfig:
    name: str
    assistant: str
    collection: str
    source_root: Path
    source_globs: tuple[str, ...]
    title: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class EmbeddingsConfig:
    provider: str
    model: str
    dimensions: int
    normalize: bool


@dataclass(frozen=True)
class ChunkingConfig:
    target_tokens: int
    overlap_tokens: int


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int
    use_hybrid: bool


@dataclass(frozen=True)
class CollectionConfig:
    name: str
    vector_size: int
    distance: str


@dataclass(frozen=True)
class VectorStoreConfig:
    backend: str
    url: str
    api_key: str | None
    timeout_seconds: float
    collection_name_template: str


def load_mvp_assistant_config() -> MvpAssistantConfig:
    path = repo_root() / "services" / "assistant-config" / "assistants" / "mvp-openrouter.yaml"
    data = _read_yaml(path)
    required = ("name", "model", "system_prompt", "knowledge_base", "retrieval_policy")
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError(f"MVP assistant config missing required fields: {', '.join(missing)}")
    return MvpAssistantConfig(
        name=str(data["name"]),
        model=str(data["model"]),
        system_prompt=str(data["system_prompt"]),
        knowledge_base=str(data["knowledge_base"]),
        retrieval_policy=str(data["retrieval_policy"]),
    )


def load_embeddings_config() -> EmbeddingsConfig:
    data = _read_yaml(repo_root() / "configs" / "rag" / "embeddings.yaml")
    embeddings = data.get("embeddings", {})
    if not isinstance(embeddings, dict):
        raise ValueError("configs/rag/embeddings.yaml must define a mapping under 'embeddings'")
    return EmbeddingsConfig(
        provider=str(embeddings.get("provider", "local")),
        model=str(embeddings.get("model", "local-hash")),
        dimensions=int(embeddings.get("dimensions", 384)),
        normalize=bool(embeddings.get("normalize", True)),
    )


def load_chunking_config() -> ChunkingConfig:
    data = _read_yaml(repo_root() / "configs" / "rag" / "chunking.yaml")
    chunking = data.get("chunking", {})
    if not isinstance(chunking, dict):
        raise ValueError("configs/rag/chunking.yaml must define a mapping under 'chunking'")
    return ChunkingConfig(
        target_tokens=max(1, int(chunking.get("target_tokens", 500))),
        overlap_tokens=max(0, int(chunking.get("overlap_tokens", 80))),
    )


def load_retrieval_config() -> RetrievalConfig:
    data = _read_yaml(repo_root() / "configs" / "rag" / "retrieval.yaml")
    retrieval = data.get("retrieval", {})
    if not isinstance(retrieval, dict):
        raise ValueError("configs/rag/retrieval.yaml must define a mapping under 'retrieval'")
    return RetrievalConfig(
        top_k=max(1, int(retrieval.get("top_k", 5))),
        use_hybrid=bool(retrieval.get("use_hybrid", False)),
    )


def load_vector_store_config() -> VectorStoreConfig:
    data = _read_yaml(repo_root() / "configs" / "rag" / "vector_store.yaml")
    vector_store = data.get("vector_store", {})
    if not isinstance(vector_store, dict):
        raise ValueError("configs/rag/vector_store.yaml must define a mapping under 'vector_store'")

    return VectorStoreConfig(
        backend=str(vector_store.get("backend", "qdrant")),
        url=os.environ.get("QDRANT_URL", str(vector_store.get("url", "http://qdrant:6333"))).rstrip("/"),
        api_key=os.environ.get("QDRANT_API_KEY", "").strip() or None,
        timeout_seconds=float(vector_store.get("timeout_seconds", 10.0)),
        collection_name_template=str(vector_store.get("collection_name_template", "{knowledge_base}")),
    )


def load_collection_config(name: str) -> CollectionConfig:
    data = _read_yaml(repo_root() / "configs" / "rag" / "collections.yaml")
    collections = data.get("collections", {})
    if not isinstance(collections, dict):
        raise ValueError("configs/rag/collections.yaml must define a mapping under 'collections'")

    config = collections.get(name)
    if not isinstance(config, dict):
        raise ValueError(f"Unknown MVP collection: {name}")

    vector_size = int(config.get("vector_size", 384))
    distance = str(config.get("distance", "Cosine"))
    return CollectionConfig(name=name, vector_size=vector_size, distance=distance)


def load_knowledge_base_config(name: str | None = None) -> KnowledgeBaseConfig:
    data = _read_yaml(repo_root() / "configs" / "rag" / "knowledge_bases.yaml")
    knowledge_bases = data.get("knowledge_bases", {})
    if not isinstance(knowledge_bases, dict):
        raise ValueError("configs/rag/knowledge_bases.yaml must define a mapping under 'knowledge_bases'")

    assistant = load_mvp_assistant_config()
    active_name = name or assistant.knowledge_base
    config = knowledge_bases.get(active_name)
    if not isinstance(config, dict):
        raise ValueError(f"Unknown MVP knowledge base: {active_name}")

    source_root = config.get("source_root", f"knowledge/sources/{active_name}/raw")
    source_globs = config.get("source_globs", ["**/*.md", "**/*.txt"])
    if not isinstance(source_globs, list) or not all(isinstance(item, str) for item in source_globs):
        raise ValueError("knowledge base source_globs must be a list of strings")

    return KnowledgeBaseConfig(
        name=active_name,
        assistant=str(config.get("assistant", assistant.name)),
        collection=str(config.get("collection", active_name)),
        source_root=_resolve_path(str(source_root)),
        source_globs=tuple(source_globs),
        title=str(config.get("title")) if config.get("title") else None,
        description=str(config.get("description")) if config.get("description") else None,
    )
