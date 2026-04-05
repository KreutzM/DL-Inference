# MVP Contract

This document defines the first runnable MVP for DL-Inference. It is the source of truth for planning and implementation until the MVP is accepted.

## Scope

The MVP is an API-first assistant platform with:

- one repo-owned gateway
- one repo-owned RAG API
- one assistant configuration
- one knowledge base
- local embeddings
- a local vector store
- OpenRouter as the only chat-completion inference backend
- non-streaming request handling first
- health, smoke, and dev-run workflow support on WSL2

## Non-goals

The MVP does not include:

- any UI
- local chat-model hosting on the Windows 10 / WSL2 RTX 3060 machine
- local large-model hosting on the later Linux 2x RTX 4090 server
- multi-assistant routing
- multi-knowledge-base orchestration
- streaming chat completions
- production hardening beyond the minimum needed to validate the path

## Target user flow

1. A developer starts the local MVP stack on WSL2.
2. The repo-owned gateway and RAG API become available.
3. One assistant is resolved from repo config.
4. One knowledge base is ingested into the vector store.
5. A non-streaming chat-completions request reaches the gateway.
6. The gateway uses the configured assistant and retrieval policy.
7. The RAG API returns retrieved sources and citations.
8. The gateway sends the final prompt to OpenRouter.
9. The response is returned with defined citation metadata.

## Required runtime components

The MVP runtime requires:

- repo-owned gateway service
- repo-owned RAG API service
- local vector store
- local embedding path
- OpenRouter connectivity for chat completion
- repo config for one assistant and one knowledge base

The MVP explicitly does not require a local LLM runtime.

## Minimal API behavior

The gateway must expose an OpenAI-compatible chat-completions path that supports:

- non-streaming requests
- assistant selection from repo config
- retrieval-augmented responses
- citation metadata in the response

The first accepted MVP request path only needs the behavior required by the documented smoke test.

## Assistant configuration expectations

The repo must define exactly one MVP assistant configuration that:

- can be resolved from repo-owned config
- references exactly one knowledge base
- declares retrieval policy and citation behavior
- targets the OpenRouter-backed chat-completion path
- does not depend on a UI for activation or editing

## Retrieval and citation expectations

The MVP retrieval path must:

- ingest one knowledge base into the vector store
- retrieve relevant chunks for the active assistant
- return sources in a stable, documented MVP format
- include citation metadata that maps answer content back to retrieved sources

The exact citation payload can be minimal, but it must be deterministic enough for smoke validation.

## Acceptance criteria

The MVP is accepted only when all of the following are true:

- A local dev stack can be started on WSL2 for the MVP path.
- One knowledge base can be ingested into the vector store.
- One assistant can be resolved from repo config.
- One non-streaming chat-completions request can complete end-to-end through the repo gateway using OpenRouter.
- Retrieval can be invoked and citations or sources are returned in the documented MVP format.
- The smoke validation for the MVP path is documented and runnable.

## Development and validation workflow

Preferred operator flow:

```bash
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli smoke
```

Relevant validation commands for MVP work:

```bash
python -m repo2ctl.cli lint
python -m repo2ctl.cli smoke
```

Implementation work should treat this document as the contract before expanding the system beyond the MVP.