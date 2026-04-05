# Local Dev

Suggested first dev stack:

- Qdrant
- LiteLLM proxy
- one inference backend (vLLM or SGLang)
- LibreChat or Open WebUI
- repo-owned gateway and RAG API

## Typical flow

```bash
cp .env.example .env
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli smoke
```

## Cross-platform operator commands

Portable Python entrypoint:

```bash
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli lint
python -m repo2ctl.cli smoke
python -m repo2ctl.cli down
```

PowerShell equivalents:

```powershell
./scripts/repo2.ps1 up-dev
./scripts/repo2.ps1 lint
./scripts/repo2.ps1 smoke
./scripts/repo2.ps1 down
```

## Path conventions

Use these canonical repo-owned service directories in docs, imports, tests, and compose files:

- `services/gateway`
- `services/rag_api`

See also `docs/development/codex-cli.md`.
