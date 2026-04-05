# Local Dev

Suggested first dev stack for the MVP:

- local vector store
- deterministic local hash embeddings
- repo-owned gateway
- repo-owned RAG API
- OpenRouter connectivity for chat completion
- one assistant and one knowledge base

`python -m repo2ctl.cli up-dev` starts the MVP stack only:

- gateway
- RAG API
- Qdrant

It does not require a UI service or a local LLM runtime.

## Typical flow

```bash
cp .env.example .env
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli smoke
python -m repo2ctl.cli mvp-acceptance
```

## MVP RAG smoke path

The first runnable RAG slice uses the checked-in `mvp-one` knowledge base and the repo-owned `services/rag_api` service.
Retrieval payloads use repo-relative `source` paths so the smoke path remains portable across machines.
The gateway consumes these retrieval results before calling OpenRouter, so the end-to-end smoke path is gateway -> RAG -> OpenRouter.

```bash
python -m repo2ctl.cli up-dev
curl -X POST http://127.0.0.1:8010/ingest \
  -H "Content-Type: application/json" \
  -d '{"assistant":"mvp-openrouter","knowledge_base":"mvp-one"}'
curl -X POST http://127.0.0.1:8010/retrieve \
  -H "Content-Type: application/json" \
  -d '{"assistant":"mvp-openrouter","knowledge_base":"mvp-one","query":"How do I reset settings in JAWS?"}'
curl -X POST http://127.0.0.1:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"mvp_openrouter_chat","messages":[{"role":"user","content":"How do I reset settings in JAWS?"}],"stream":false}'
```

For operators validating the full MVP path repeatedly, the recommended single command is:

```bash
python -m repo2ctl.cli mvp-acceptance
```

It starts the MVP stack, waits for both health endpoints, ingests `mvp-one`, checks retrieval, and verifies a non-streaming gateway response with citation metadata.

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
