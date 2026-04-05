# Windows / PowerShell Dev Notes

This repo is designed so that the **operator workflow** is usable from both:

- Bash on Linux/macOS
- PowerShell on Windows

## Important scope boundary

- **Repo operations** such as smoke tests, Docker Compose startup, logs, health checks, and helper scripts are intended to be cross-platform.
- **Local GPU model serving** with stacks like vLLM or SGLang remains primarily a **Linux-first** target.
- On Windows, the practical options are usually:
  - Docker Desktop with WSL2
  - a remote Linux GPU server
  - or using OpenRouter/cloud backends while keeping the same repo and assistant stack

## Recommended entrypoints

Prefer the Python operator CLI:

```powershell
python -m repo2ctl.cli help
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli smoke
```

Convenience wrappers are also available:

```powershell
./scripts/repo2.ps1 up-dev
./scripts/repo2.ps1 smoke
./deploy/scripts/healthcheck.ps1
```

## Environment setup

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Docker notes

- Install Docker Desktop
- Enable WSL2 integration if you want Linux containers locally
- For OpenRouter-backed testing, Windows works well because the heavy inference stays remote

## Best use under Windows

The strongest Windows-friendly path for this repo's MVP is:

- run the repo-owned gateway, RAG API, and Qdrant locally
- use OpenRouter as the only chat-completion backend
- keep the local Linux GPU path and UI services for later phases
