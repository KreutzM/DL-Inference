from __future__ import annotations

from fastapi.testclient import TestClient

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


def test_chat_completions_maps_openrouter_response(monkeypatch):
    client = TestClient(app)
    dummy = DummyOpenRouterClient()
    monkeypatch.setattr("services.gateway.app.main.get_openrouter_client", lambda: dummy)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

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
    assert dummy.calls[0]["model"] == "mvp_openrouter_chat"


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
