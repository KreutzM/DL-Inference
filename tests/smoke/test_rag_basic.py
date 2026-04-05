from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from services.rag_api.app.main import app
from services.rag_api.app import rag


def _write_fixture_repo(root: Path) -> None:
    (root / "configs" / "rag").mkdir(parents=True, exist_ok=True)
    (root / "services" / "assistant-config" / "assistants").mkdir(parents=True, exist_ok=True)
    (root / "knowledge" / "sources" / "mvp-one" / "raw").mkdir(parents=True, exist_ok=True)
    (root / "knowledge" / "processed" / "vector_store").mkdir(parents=True, exist_ok=True)

    (root / "configs" / "rag" / "embeddings.yaml").write_text(
        "\n".join(
            [
                "embeddings:",
                "  provider: local",
                "  model: deterministic-local-hash-384",
                "  dimensions: 64",
                "  normalize: true",
            ]
        ),
        encoding="utf-8",
    )
    (root / "configs" / "rag" / "chunking.yaml").write_text(
        "\n".join(
            [
                "chunking:",
                "  target_tokens: 40",
                "  overlap_tokens: 10",
            ]
        ),
        encoding="utf-8",
    )
    (root / "configs" / "rag" / "retrieval.yaml").write_text(
        "\n".join(
            [
                "retrieval:",
                "  top_k: 3",
                "  use_hybrid: false",
            ]
        ),
        encoding="utf-8",
    )
    (root / "configs" / "rag" / "vector_store.yaml").write_text(
        "\n".join(
            [
                "vector_store:",
                "  backend: qdrant",
                "  collection_name_template: \"{knowledge_base}\"",
                "  timeout_seconds: 10",
            ]
        ),
        encoding="utf-8",
    )
    (root / "configs" / "rag" / "collections.yaml").write_text(
        "\n".join(
            [
                "collections:",
                "  mvp-one:",
                "    vector_size: 64",
                "    distance: Cosine",
            ]
        ),
        encoding="utf-8",
    )
    (root / "configs" / "rag" / "knowledge_bases.yaml").write_text(
        "\n".join(
            [
                "knowledge_bases:",
                "  mvp-one:",
                "    assistant: mvp-openrouter",
                "    collection: mvp-one",
                "    source_root: knowledge/sources/mvp-one/raw",
                "    source_globs:",
                "      - \"**/*.md\"",
                "      - \"**/*.txt\"",
            ]
        ),
        encoding="utf-8",
    )
    (root / "services" / "assistant-config" / "assistants" / "mvp-openrouter.yaml").write_text(
        "\n".join(
            [
                "name: mvp-openrouter",
                "model: mvp_openrouter_chat",
                "system_prompt: services/assistant-config/system-prompts/jaws_support.md",
                "knowledge_base: mvp-one",
                "retrieval_policy: enabled",
            ]
        ),
        encoding="utf-8",
    )
    (root / "knowledge" / "sources" / "mvp-one" / "raw" / "jaws-support-mvp.md").write_text(
        "\n".join(
            [
                "# MVP JAWS Support Knowledge Base",
                "",
                "If a user asks how to reset JAWS settings, close JAWS, rename the settings folder, and restart JAWS.",
            ]
        ),
        encoding="utf-8",
    )


class FakeVectorStore:
    def __init__(self) -> None:
        self.collections: dict[str, dict[str, object]] = {}

    def ensure_collection(self, collection) -> None:  # type: ignore[no-untyped-def]
        self.collections.setdefault(collection.name, {"collection": collection, "records": []})

    def upsert(self, collection_name: str, records: list[dict[str, object]]) -> None:
        self.collections.setdefault(collection_name, {"records": []})
        self.collections[collection_name]["records"] = list(records)

    def search(self, collection_name: str, vector: list[float], limit: int) -> list[dict[str, object]]:
        records = list(self.collections.get(collection_name, {}).get("records", []))
        scored: list[dict[str, object]] = []
        for record in records:
            embedding = [float(value) for value in record["embedding"]]
            score = sum(a * b for a, b in zip(vector, embedding))
            scored.append({"score": score, "payload": record})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:limit]


def test_rag_basic(monkeypatch, tmp_path) -> None:
    _write_fixture_repo(tmp_path)
    monkeypatch.setenv("DL_INFERENCE_REPO_ROOT", str(tmp_path))
    fake_store = FakeVectorStore()
    monkeypatch.setattr(rag, "build_vector_store_client", lambda config: fake_store)

    client = TestClient(app)
    assert client.get("/health").json()["service"] == "rag_api"

    ingest_response = client.post(
        "/ingest",
        json={
            "assistant": "mvp-openrouter",
            "knowledge_base": "mvp-one",
        },
    )
    assert ingest_response.status_code == 200

    retrieve_response = client.post(
        "/retrieve",
        json={
            "query": "How do I reset settings in JAWS?",
            "assistant": "mvp-openrouter",
            "knowledge_base": "mvp-one",
        },
    )
    assert retrieve_response.status_code == 200
    payload = retrieve_response.json()
    assert payload["sources"]
    assert payload["citations"]
    assert payload["sources"][0]["source"] == "knowledge/sources/mvp-one/raw/jaws-support-mvp.md"
    assert not payload["sources"][0]["source"].startswith("/")
