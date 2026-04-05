from __future__ import annotations

from services.rag_api.app.config import (
    load_collection_config,
    load_embeddings_config,
    load_knowledge_base_config,
)


def test_mvp_rag_collection_matches_embedding_dimensions() -> None:
    embeddings = load_embeddings_config()
    kb = load_knowledge_base_config("mvp-one")
    collection = load_collection_config(kb.collection)

    assert embeddings.provider == "local"
    assert embeddings.model == "deterministic-local-hash-384"
    assert embeddings.dimensions == 384
    assert collection.vector_size == embeddings.dimensions
    assert collection.distance == "Cosine"


def test_mvp_knowledge_base_points_to_single_collection() -> None:
    kb = load_knowledge_base_config("mvp-one")

    assert kb.name == "mvp-one"
    assert kb.assistant == "mvp-openrouter"
    assert kb.collection == "mvp-one"
    assert kb.source_root.as_posix().endswith("knowledge/sources/mvp-one/raw")
