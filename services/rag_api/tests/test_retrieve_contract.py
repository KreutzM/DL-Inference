from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from services.rag_api.app.main import app


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
                "  model: local-hash",
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
                "  backend: local-json",
                "  root: knowledge/processed/vector_store",
                "  filename_template: \"{knowledge_base}.json\"",
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
                "retrieval_policy: deferred",
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
                "This seeded knowledge base exists only for the first runnable RAG slice.",
            ]
        ),
        encoding="utf-8",
    )


def test_ingest_and_retrieve_contract(monkeypatch, tmp_path) -> None:
    _write_fixture_repo(tmp_path)
    monkeypatch.setenv("DL_INFERENCE_REPO_ROOT", str(tmp_path))

    client = TestClient(app)

    ingest_response = client.post(
        "/ingest",
        json={
            "assistant": "mvp-openrouter",
            "knowledge_base": "mvp-one",
        },
    )
    assert ingest_response.status_code == 200
    ingest_payload = ingest_response.json()
    assert ingest_payload["status"] == "ok"
    assert ingest_payload["knowledge_base"] == "mvp-one"
    assert ingest_payload["documents_ingested"] == 1
    assert ingest_payload["chunks_indexed"] >= 1
    assert ingest_payload["vector_store_path"].endswith("knowledge/processed/vector_store/mvp-one.json")

    retrieve_response = client.post(
        "/retrieve",
        json={
            "query": "How do I reset settings in JAWS?",
            "assistant": "mvp-openrouter",
            "knowledge_base": "mvp-one",
            "top_k": 2,
        },
    )
    assert retrieve_response.status_code == 200
    payload = retrieve_response.json()
    assert payload["status"] == "ok"
    assert payload["assistant"] == "mvp-openrouter"
    assert payload["knowledge_base"] == "mvp-one"
    assert payload["sources"]
    assert payload["citations"]
    assert payload["sources"][0]["source_id"] == payload["citations"][0]["source_id"]
    assert "reset jaws settings" in payload["sources"][0]["text"]


def test_retrieve_rejects_unknown_assistant(monkeypatch, tmp_path) -> None:
    _write_fixture_repo(tmp_path)
    monkeypatch.setenv("DL_INFERENCE_REPO_ROOT", str(tmp_path))

    client = TestClient(app)
    response = client.post(
        "/retrieve",
        json={
            "query": "How do I reset settings in JAWS?",
            "assistant": "unknown",
            "knowledge_base": "mvp-one",
        },
    )
    assert response.status_code == 400
    assert "Unknown MVP assistant" in response.json()["detail"]
