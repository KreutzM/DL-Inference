from __future__ import annotations

from time import time
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .assistant_config import assistant_summary, load_mvp_assistant, load_mvp_system_prompt_text
from .openrouter import OpenRouterClient, load_openrouter_settings
from .rag_client import RagApiClient, load_rag_api_settings
from .routing import list_models, load_mvp_model_route, resolve_model

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


def get_rag_client() -> RagApiClient:
    return RagApiClient(load_rag_api_settings())


def _latest_user_message(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    raise HTTPException(status_code=400, detail="messages must include a non-empty user message")


def _format_retrieved_context(sources: list[dict[str, object]]) -> str:
    if not sources:
        return "No retrieved evidence was available for this answer."

    lines = ["Retrieved evidence:"]
    for index, source in enumerate(sources, start=1):
        lines.append(
            f"{index}. source_id={source.get('source_id')} document_id={source.get('document_id')} "
            f"chunk_id={source.get('chunk_id')} source={source.get('source')} "
            f"score={source.get('score')} text={source.get('text')}"
        )
    return "\n".join(lines)


def _build_upstream_messages(
    system_prompt: str,
    retrieved_context: str,
    request_messages: list[ChatMessage],
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": retrieved_context},
        *[message.model_dump() for message in request_messages],
    ]


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest) -> dict[str, object]:
    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming is not supported in the MVP gateway path.")
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages must contain at least one item")

    try:
        selected_model = resolve_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    assistant = load_mvp_assistant()
    model_route = load_mvp_model_route()
    if assistant.model != selected_model or model_route.alias != assistant.model:
        raise HTTPException(status_code=400, detail="Requested model does not match the MVP assistant config")

    system_prompt = load_mvp_system_prompt_text()
    user_query = _latest_user_message(request.messages)
    retrieval_payload: dict[str, object] = {"sources": [], "citations": [], "meta": {}}

    if assistant.retrieval_policy == "enabled":
        try:
            retrieval_payload = get_rag_client().retrieve(
                query=user_query,
                assistant=assistant.name,
                knowledge_base=assistant.knowledge_base,
                top_k=3,
            )
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except httpx.RequestError as exc:  # type: ignore[name-defined]
            raise HTTPException(status_code=503, detail=f"RAG API request failed: {exc}") from exc
        except Exception as exc:  # pragma: no cover - surfaced in focused tests
            raise HTTPException(status_code=502, detail=f"RAG API request failed: {exc}") from exc

    retrieved_context = _format_retrieved_context([dict(item) for item in retrieval_payload.get("sources", [])])
    upstream_messages = _build_upstream_messages(system_prompt, retrieved_context, request.messages)
    openrouter_payload = {
        "model": model_route.provider_model_id,
        "messages": upstream_messages,
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
        "model": model_route.alias,
        "assistant": assistant_summary(),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": first_choice.get("finish_reason", "stop"),
            }
        ],
        "citations": retrieval_payload.get("citations", []),
        "retrieval": {
            "assistant": retrieval_payload.get("assistant", assistant.name),
            "knowledge_base": retrieval_payload.get("knowledge_base", assistant.knowledge_base),
            "sources": retrieval_payload.get("sources", []),
            "meta": retrieval_payload.get("meta", {}),
        },
        "usage": {
            "prompt_tokens": int((upstream.get("usage") or {}).get("prompt_tokens", 0)),
            "completion_tokens": int((upstream.get("usage") or {}).get("completion_tokens", 0)),
            "total_tokens": int((upstream.get("usage") or {}).get("total_tokens", 0)),
        },
    }
