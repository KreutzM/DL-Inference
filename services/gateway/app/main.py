from __future__ import annotations

from time import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .assistant_config import assistant_summary, load_mvp_assistant
from .openrouter import OpenRouterClient, load_openrouter_settings
from .routing import list_models, resolve_model

app = FastAPI(title="Repo2 Gateway", version="0.1.0")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float | None = None
    stream: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "gateway"}


@app.get("/v1/models")
def models() -> dict[str, object]:
    return {"object": "list", "data": list_models()}


def get_openrouter_client() -> OpenRouterClient:
    return OpenRouterClient(load_openrouter_settings())


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest) -> dict[str, object]:
    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming is not supported in the MVP gateway path.")
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages must contain at least one item")
    if not any(message.role == "user" for message in request.messages):
        raise HTTPException(status_code=400, detail="messages must include a user message")

    try:
        selected_model = resolve_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    assistant = load_mvp_assistant()
    if assistant.model != selected_model:
        raise HTTPException(status_code=400, detail="Requested model does not match the MVP assistant config")

    openrouter_payload = {
        "model": assistant.model,
        "messages": [message.model_dump() for message in request.messages],
        "temperature": request.temperature,
        "stream": False,
    }

    try:
        upstream = get_openrouter_client().chat_completions(openrouter_payload)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - surfaced in focused tests
        raise HTTPException(status_code=502, detail=f"OpenRouter request failed: {exc}") from exc

    choices = upstream.get("choices") or []
    first_choice = choices[0] if choices else {}
    message = first_choice.get("message") or {}
    content = str(message.get("content", ""))

    return {
        "id": f"chatcmpl-{uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time()),
        "model": assistant.model,
        "assistant": assistant_summary(),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": first_choice.get("finish_reason", "stop"),
            }
        ],
        "usage": {
            "prompt_tokens": int((upstream.get("usage") or {}).get("prompt_tokens", 0)),
            "completion_tokens": int((upstream.get("usage") or {}).get("completion_tokens", 0)),
            "total_tokens": int((upstream.get("usage") or {}).get("total_tokens", 0)),
        },
    }
