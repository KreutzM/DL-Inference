# AGENTS.md

This repository is a monorepo scaffold for a self-hosted inference + RAG platform. It is intentionally Linux-first for GPU serving, but the repo operator workflow should stay usable from both Bash and PowerShell.

## Primary objective

Improve the repository while preserving these architectural goals:

1. **OpenAI-compatible edge API**
2. **Local inference first**
3. **Repo-owned RAG logic**
4. **Config-driven assistants**
5. **Clear separation between versioned knowledge and runtime data**

## Key directories

- `services/` — repo-owned code
- `configs/` — declarative system configuration
- `deploy/` — docker compose, reverse proxy, systemd, deployment helpers
- `knowledge/` — versioned knowledge assets
- `data/` — runtime volumes and persistent state
- `tests/` — smoke, integration, regression tests
- `docs/` — architecture and operations docs

## What counts as high-value work

Prioritize work that:

- improves the local inference path
- improves API compatibility and routing clarity
- improves RAG quality and traceability
- improves deployment reproducibility
- improves testability and operational safety

## Constraints

- Do not add secrets to the repository.
- Do not hardcode machine-specific absolute paths unless they are examples.
- Do not silently move core logic into vendor tools.
- Prefer adding or updating docs when changing architecture.
- Keep compose files and config examples synchronized.

## Expected validation steps

Before considering work complete, run what is relevant:

```bash
make fmt
make lint
make test
make smoke
```

If a target is not yet fully implemented, update the corresponding docs or TODO markers.

## Coding guidance

- Python code should be typed where practical.
- Service stubs should expose clear interfaces.
- Config files should stay explicit and readable.
- Preserve simple, predictable names.
- Prefer a **portable Python entrypoint** for operator flows when possible.
- If you add a Bash helper for a common repo task, add a matching `.ps1` variant or route both through `repo2ctl`.

## Completion standard

A good change usually includes:

- code or config changes
- documentation updates where needed
- at least one test or smoke validation improvement
