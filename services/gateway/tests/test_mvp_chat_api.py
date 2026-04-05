from __future__ import annotations

from fastapi.testclient import TestClient
import httpx

from services.gateway.app.assistant_config import load_mvp_system_prompt_text
from services.gateway.app.main import app


class DummyOpenRouterClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def chat_completions(self, payload: dict[str, object]) -> dict[str, object]:
        self.calls.append(payload)
        return {
            "id": "chatcmpl-upstream",
            "object": "chat.completion",
            "created": 123,
            "model": "openai/gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello from OpenRouter"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10},
        }


class DummyRagClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def retrieve(self, *, query: str, assistant: str, knowledge_base: str, top_k: int = 3) -> dict[str, object]:
        self.calls.append(
            {
                "query": query,
                "assistant": assistant,
                "knowledge_base": knowledge_base,
                "top_k": top_k,
            }
        )
        return {
            "status": "ok",
            "assistant": assistant,
            "knowledge_base": knowledge_base,
            "sources": [
                {
                    "source_id": "mvp-one:jaws-support-mvp.md#chunk-1",
                    "document_id": "jaws-support-mvp.md",
                    "chunk_id": "jaws-support-mvp.md#chunk-1",
                    "score": 0.99,
                    "source": "knowledge/sources/mvp-one/raw/jaws-support-mvp.md",
                    "title": "Jaws Support Mvp",
                    "text": "reset settings by renaming the folder",
                    "metadata": {"relative_path": "jaws-support-mvp.md"},
                }
            ],
            "citations": [
                {
                    "citation_id": "cite-1",
                    "source_id": "mvp-one:jaws-support-mvp.md#chunk-1",
                    "document_id": "jaws-support-mvp.md",
                    "chunk_id": "jaws-support-mvp.md#chunk-1",
                    "source": "knowledge/sources/mvp-one/raw/jaws-support-mvp.md",
                    "score": 0.99,
                }
            ],
            "meta": {"collection": "mvp-one", "returned_chunks": 1},
        }


def test_chat_completions_maps_openrouter_response(monkeypatch):
    client = TestClient(app)
    dummy = DummyOpenRouterClient()
    rag = DummyRagClient()
    monkeypatch.setattr("services.gateway.app.main.get_openrouter_client", lambda: dummy)
    monkeypatch.setattr("services.gateway.app.main.get_rag_client", lambda: rag)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("RAG_API_URL", "http://rag_api:8010")

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "mvp_openrouter_chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "chat.completion"
    assert payload["model"] == "mvp_openrouter_chat"
    assert payload["assistant"]["metadata"]["assistant"] == "mvp-openrouter"
    assert payload["choices"][0]["message"]["content"] == "Hello from OpenRouter"
    assert payload["usage"] == {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10}
    assert payload["citations"][0]["source_id"] == "mvp-one:jaws-support-mvp.md#chunk-1"
    assert payload["retrieval"]["sources"][0]["source"] == "knowledge/sources/mvp-one/raw/jaws-support-mvp.md"
    assert rag.calls[0] == {
        "query": "Hello",
        "assistant": "mvp-openrouter",
        "knowledge_base": "mvp-one",
        "top_k": 3,
    }
    assert dummy.calls[0]["model"] == "openai/gpt-4o-mini"
    assert dummy.calls[0]["messages"][0]["role"] == "system"
    assert dummy.calls[0]["messages"][0]["content"] == load_mvp_system_prompt_text()
    assert "Retrieved evidence:" in dummy.calls[0]["messages"][1]["content"]
    assert "source_id=mvp-one:jaws-support-mvp.md#chunk-1" in dummy.calls[0]["messages"][1]["content"]
    assert dummy.calls[0]["messages"][2] == {"role": "user", "content": "Hello"}


def test_chat_completions_rejects_streaming():
    client = TestClient(app)
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "mvp_openrouter_chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True,
        },
    )
    assert response.status_code == 400
    assert "Streaming is not supported" in response.json()["detail"]


def test_chat_completions_rejects_missing_api_key(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(
        "services.gateway.app.main.get_rag_client",
        lambda: DummyRagClient(),
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "mvp_openrouter_chat",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )

    assert response.status_code == 500
    assert "OPENROUTER_API_KEY is required" in response.json()["detail"]


def test_chat_completions_rejects_unknown_model(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "not-a-model",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )

    assert response.status_code == 400
    assert "Unknown model: not-a-model" in response.json()["detail"]


def test_chat_completions_rejects_rag_connectivity_failure(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    class BrokenRagClient:
        def retrieve(self, **kwargs):  # type: ignore[no-untyped-def]
            raise httpx.RequestError("no route", request=httpx.Request("POST", "http://rag_api:8010/retrieve"))

    monkeypatch.setattr("services.gateway.app.main.get_rag_client", lambda: BrokenRagClient())

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "mvp_openrouter_chat",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )

    assert response.status_code == 503
    assert "RAG API request failed" in response.json()["detail"]
