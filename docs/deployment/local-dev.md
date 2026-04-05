# Local Dev

Suggested first dev stack:

- local vector store
- deterministic local hash embeddings
- repo-owned gateway and RAG API
- OpenRouter connectivity for chat completion
- one assistant and one knowledge base

## Typical flow

```bash
cp .env.example .env
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli smoke
```

## MVP RAG smoke path

The first runnable RAG slice uses the checked-in `mvp-one` knowledge base and the repo-owned `services/rag_api` service.
Retrieval payloads use repo-relative `source` paths so the smoke path remains portable across machines.

```bash
python -m repo2ctl.cli up-dev
curl -X POST http://127.0.0.1:8010/ingest \
  -H "Content-Type: application/json" \
  -d '{"assistant":"mvp-openrouter","knowledge_base":"mvp-one"}'
curl -X POST http://127.0.0.1:8010/retrieve \
  -H "Content-Type: application/json" \
  -d '{"assistant":"mvp-openrouter","knowledge_base":"mvp-one","query":"How do I reset settings in JAWS?"}'
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
