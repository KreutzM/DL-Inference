from __future__ import annotations

from time import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest) -> dict[str, object]:
    if request.stream:
        raise HTTPException(status_code=501, detail="Streaming is not implemented in this scaffold yet.")

    try:
        selected_model = resolve_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    last_user_message = next(
        (message.content for message in reversed(request.messages) if message.role == "user"),
        "",
    )
    content = (
        "Gateway scaffold placeholder. "
        f"Selected model: {selected_model}. "
        f"Last user message length: {len(last_user_message)}."
    )

    return {
        "id": f"chatcmpl-{uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time()),
        "model": selected_model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }
