# System Overview

This repository defines a self-hosted assistant platform with:

- one or more local inference servers
- a stable gateway layer
- a repo-owned RAG API
- assistant configurations stored as files
- one or more UIs for testing and operations

## Core principle

The platform should remain **OpenAI-compatible at the edge** while staying flexible internally.

## Major subsystems

- `services/gateway` — public API surface and routing facade
- `services/inference-manager` — future model profile awareness and launcher orchestration
- `services/rag_api` — ingestion, retrieval, reranking, and citation assembly
- `services/assistant-config` — assistant prompts, templates, and policies
- `configs/` — the declarative truth of runtime behavior
- `deploy/` — composition and environment-specific deployment

## Canonical implementation paths

The repo-owned service roots are:

- `services/gateway`
- `services/rag_api`

Legacy paths such as `services/gateway_pkg`, `services/rag_api_pkg`, and `services/rag-api` are deprecated and should be removed from active use.
