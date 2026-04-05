from services.rag_api.app.config import load_collection_config, load_embeddings_config


def test_rag_qdrant_config_is_mvp_ready() -> None:
    embeddings = load_embeddings_config()
    collection = load_collection_config("mvp-one")

    assert embeddings.dimensions == collection.vector_size == 384
    assert collection.distance == "Cosine"
