# Local Dev

Suggested first dev stack for the MVP:

- local vector store
- local embeddings
- repo-owned gateway
- repo-owned RAG API
- OpenRouter connectivity for chat completion
- one assistant and one knowledge base

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

See also `docs/product/mvp-contract.md` and `docs/development/codex-cli.md`.