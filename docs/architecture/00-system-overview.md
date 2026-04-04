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

- `services/gateway` — public API surface and routing façade
- `services/inference-manager` — model profile awareness and launcher orchestration
- `services/rag-api` — ingestion, retrieval, reranking, citation assembly
- `services/assistant-config` — assistant prompts, templates, policies
- `configs/` — the declarative truth of runtime behavior
- `deploy/` — composition and environment-specific deployment
