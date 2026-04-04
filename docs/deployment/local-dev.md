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
make up-dev
make smoke
```


## Cross-platform operator commands

Portable Python entrypoint:

```bash
python -m repo2ctl.cli up-dev
python -m repo2ctl.cli smoke
python -m repo2ctl.cli down
```

PowerShell equivalents:

```powershell
./scripts/repo2.ps1 up-dev
./scripts/repo2.ps1 smoke
./scripts/repo2.ps1 down
```

See also `docs/deployment/windows-dev.md`.
