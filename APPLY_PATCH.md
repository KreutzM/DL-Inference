# Apply this patch

This ZIP is an overlay patch for the repository root.

## Apply

From the repository root:

Bash / Linux / macOS

```bash
unzip /path/to/DL-Inference-codex-prep-patch.zip -d .
```

PowerShell / Windows

```powershell
Expand-Archive -Path .\DL-Inference-codex-prep-patch.zip -DestinationPath .
```

## Then review

```bash
git status
git diff --stat
python -m repo2ctl.cli lint
python -m repo2ctl.cli smoke
```

## What this patch changes

- improves `AGENTS.md` for the two-model Codex workflow
- adds/updates custom agents under `.codex/agents/`
- expands Codex docs and prompt templates
- upgrades `repo2ctl review-info` so Git metadata can be scaffolded automatically
- adds small tests for the Codex-prep surface
- makes `scripts/lint_repo.py` validate the Codex setup without failing on the repo's current transitional service-path state
