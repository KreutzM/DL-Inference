# System Overview

This repository defines a self-hosted assistant platform with:

- an API-first MVP centered on OpenRouter-backed chat completion
- a stable gateway layer
- a repo-owned RAG API
- assistant configurations stored as files
- no UI requirement in the MVP

## Core principle

The platform should remain **OpenAI-compatible at the edge** while staying flexible internally.
The active MVP contract is documented in `docs/product/mvp-contract.md`.

## Major subsystems

- `services/gateway` — public API surface and routing facade
- `services/inference-manager` — future model profile awareness and launcher orchestration
- `services/rag_api` — ingestion, retrieval, reranking, and citation assembly
- `services/assistant-config` — assistant prompts, templates, and policies
- `configs/` — the declarative truth of runtime behavior
- `deploy/` — composition and environment-specific deployment

## Canonical implementation paths

The repo-owned service roots are:

- `services/assistant-config`
- `services/gateway`
- `services/inference-manager`
- `services/ops-api`
- `services/rag_api`
- `services/ui-lib`