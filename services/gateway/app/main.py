from fastapi import FastAPI

from .routing import list_models

app = FastAPI(title="Repo2 Gateway", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "gateway"}


@app.get("/v1/models")
def models() -> dict:
    return {"object": "list", "data": list_models()}


@app.post("/v1/chat/completions")
def chat_completions() -> dict:
    return {
        "id": "chatcmpl-placeholder",
        "object": "chat.completion",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "TODO"}, "finish_reason": "stop"}],
        "model": "local-default",
    }
