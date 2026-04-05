# Repo 2 — Offline Inference & RAG Platform

A Linux-first but Windows/PowerShell-friendly monorepo for a self-hosted assistant platform with:

- an API-first MVP that uses OpenRouter for chat completion
- an OpenAI/OpenRouter-compatible API surface
- Custom-GPT-like assistants with system prompts, knowledge bases, and configurable behavior
- a production-oriented RAG stack
- a Codex CLI friendly repo structure

## Primary goals

1. Ship a precise, runnable MVP contract for API-first assistant workflows.
2. Provide a clean gateway layer with repo-owned routing and repo-owned RAG.
3. Support assistant configurations, knowledge bases, and retrieval pipelines as first-class repo artifacts.
4. Keep the repository ready for iterative implementation with Codex CLI.

## Recommended stack

- Inference: OpenRouter for the MVP chat-completion path
- Gateway: repo-owned gateway facade
- RAG: repo-owned RAG API plus local embeddings and vector store
- Main UI: out of MVP scope
- Secondary UI / internal testing: out of MVP scope
- Vector DB: Qdrant
- RAG orchestration: LlamaIndex
- Reverse proxy: Caddy (default) or Nginx
- Observability: Prometheus + Grafana + Loki + OpenTelemetry

## Repo status

This repository is an implementation scaffold. It contains:

- a complete top-level repo structure
- starter configs
- service skeletons
- deployment compose files
- Codex-friendly instructions
- evaluation and observability placeholders

It does not yet contain a full production implementation.

## Codex CLI workflow

Default usage in this repo:

- primary implementation model: `gpt-5.4-mini`
- escalation model for planning/review: `gpt-5.4`

Repo-specific Codex configuration lives in:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/`
- `docs/development/codex-cli.md`
- `docs/development/prompt-templates.md`

Recommended commands:

```bash
python -m repo2ctl.cli fmt
python -m repo2ctl.cli lint
python -m repo2ctl.cli test
python -m repo2ctl.cli smoke
python -m repo2ctl.cli review-info --base origin/main
```

## Current service-path layout

The repo uses canonical service roots under `services/` and treats them as the active path contract:

- `services/assistant-config/`
- `services/gateway/`
- `services/inference-manager/`
- `services/ops-api/`
- `services/rag_api/`
- `services/ui-lib/`

Codex guidance:
- keep changes aligned with the current service-root layout
- avoid introducing parallel roots
- only migrate paths when a task explicitly asks for it
- if a migration is requested, update code, imports, tests, Dockerfiles, compose files, scripts, and docs together
- do not treat older path names as active guidance

## Quick start

### 1. Review the repo instructions

Read:

- `AGENTS.md`
- `docs/architecture/00-system-overview.md`
- `docs/deployment/local-dev.md`
- `docs/development/codex-cli.md`

### 2. Prepare environment

Bash / Linux / macOS

```bash
cp .env.example .env
```

PowerShell / Windows

```powershell
Copy-Item .env.example .env
```

Fill in required values.

### 3. Start a minimal local stack

Portable Python entrypoint (recommended)

```bash
python -m repo2ctl.cli up-dev
```

PowerShell wrapper

```powershell
./scripts/repo2.ps1 up-dev
```

GNU Make (optional, mainly Linux/macOS)

```bash
make up-dev
```

### 4. Run smoke checks

```bash
python -m repo2ctl.cli smoke
```

```powershell
./scripts/repo2.ps1 smoke
```

## Suggested first implementation milestones

1. Read `docs/product/mvp-contract.md`.
2. Bring up the repo-owned gateway and RAG API around the MVP path.
3. Implement the RAG ingest/retrieve path in the active repo-owned RAG service tree.
4. Add one real assistant config and one knowledge base.
5. Validate the non-streaming OpenRouter-backed chat-completions flow.

## Directory map

- `docs/` — architecture, product, deployment, development docs
- `deploy/` — compose stacks, systemd, reverse proxy, deployment scripts
- `configs/` — declarative config for inference, routing, RAG, assistants, policies
- `services/` — repo-owned code and APIs
- `knowledge/` — versioned knowledge sources and evaluation assets
- `data/` — runtime state and persistent volumes
- `eval/` — evaluation harness and reports
- `observability/` — metrics, traces, logs
- `scripts/` — operator scripts and utilities
- `tests/` — smoke, integration, regression

## Design rules

- Keep repo-owned logic in `services/`, not inside third-party tools.
- Treat LibreChat and Open WebUI as pluggable UIs, not the core system.
- Keep knowledge artifacts versioned and separate from runtime data.
- Prefer declarative config over hidden UI settings.
- Keep the stack OpenAI-compatible at the edge to simplify switching providers.

## Cross-platform notes

- The repo keeps Python as the portable operator entrypoint via `python -m repo2ctl.cli ...`.
- Bash scripts remain available for Linux-first operation.
- PowerShell equivalents are provided for the main operator flows in `scripts/*.ps1` and `deploy/scripts/*.ps1`.
- Linux-only GPU serving remains the primary target for local inference backends like vLLM and SGLang. Under Windows, the practical path is usually Docker Desktop + WSL2 or a remote Linux GPU server.
