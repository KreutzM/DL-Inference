# Repo 2 — Offline Inference & RAG Platform

A Linux-first but Windows/PowerShell-friendly monorepo for a self-hosted assistant platform with:

- local multi-GPU inference on **2x RTX 4090**
- an **OpenAI/OpenRouter-compatible API surface**
- **Custom-GPT-like assistants** with system prompts, knowledge bases, and configurable behavior
- a production-oriented **RAG stack**
- Codex CLI friendly repo structure

## Primary goals

1. Run strong local models (initially Qwen-class, optionally OSS-class) behind a stable API.
2. Provide a clean gateway layer that can route to local backends and optional cloud backends.
3. Support assistant configurations, knowledge bases, and retrieval pipelines as first-class repo artifacts.
4. Keep the repository ready for iterative implementation with Codex CLI.

## Recommended stack

- **Inference:** vLLM and/or SGLang
- **Gateway:** LiteLLM Proxy
- **Main UI:** LibreChat
- **Secondary UI / internal testing:** Open WebUI
- **Vector DB:** Qdrant
- **RAG orchestration:** LlamaIndex
- **Reverse proxy:** Caddy (default) or Nginx
- **Observability:** Prometheus + Grafana + Loki + OpenTelemetry

## Repo status

This repository is a **base version / implementation scaffold**.
It contains:

- a complete top-level repo structure
- starter configs
- service skeletons
- deployment compose files
- Codex-friendly instructions
- evaluation and observability placeholders

It does **not** yet contain a full production implementation.

## Quick start

### 1. Review the repo instructions

Read:

- `AGENTS.md`
- `docs/architecture/00-system-overview.md`
- `docs/deployment/local-dev.md`

### 2. Prepare environment

**Bash / Linux / macOS**

```bash
cp .env.example .env
```

**PowerShell / Windows**

```powershell
Copy-Item .env.example .env
```

Fill in required values.

### 3. Start a minimal local stack

**Portable Python entrypoint (recommended)**

```bash
python -m repo2ctl.cli up-dev
```

**PowerShell wrapper**

```powershell
./scripts/repo2.ps1 up-dev
```

**GNU Make (optional, mainly Linux/macOS)**

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

1. Bring up Qdrant, LiteLLM, and a minimal API gateway.
2. Add one local inference backend (vLLM first or SGLang first).
3. Implement the RAG ingest/retrieve path in `services/rag-api`.
4. Wire LibreChat to the gateway.
5. Add one real assistant config (for example `jaws-support.yaml`).

## Directory map

- `docs/` — architecture, product, deployment, API docs
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

- Keep **repo-owned logic** in `services/`, not inside third-party tools.
- Treat **LibreChat** and **Open WebUI** as pluggable UIs, not the core system.
- Keep **knowledge artifacts** versioned and separate from runtime data.
- Prefer **declarative config** over hidden UI settings.
- Keep the stack **OpenAI-compatible** at the edge to simplify switching providers.


## Cross-platform notes

- The repo keeps **Python** as the portable operator entrypoint via `python -m repo2ctl.cli ...`.
- Bash scripts remain available for Linux-first operation.
- PowerShell equivalents are provided for the main operator flows in `scripts/*.ps1` and `deploy/scripts/*.ps1`.
- Linux-only GPU serving remains the primary target for local inference backends like vLLM and SGLang. Under Windows, the practical path is usually Docker Desktop + WSL2 or a remote Linux GPU server.
