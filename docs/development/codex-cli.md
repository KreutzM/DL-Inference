# Codex CLI workflow for this repo

This repository is prepared for a two-model Codex workflow:

- **Primary implementation model:** `gpt-5.4-mini`
- **Secondary heavy/review model:** `gpt-5.4`

## Why this split

Use `gpt-5.4-mini` for fast, well-scoped implementation work.
Use `gpt-5.4` for architecture, planning, deep debugging, and validating whether a Codex run actually did the right thing.

## Repo-level controls

The repo guidance lives in:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`

## Recommended profiles

- default / `implement` — `gpt-5.4-mini`
- `review` — `gpt-5.4`
- `research` — `gpt-5.4` with live web search
- `mini-fast` — very fast low-depth implementation profile

## Prompting guidance for `gpt-5.4-mini`

For best results, keep tasks explicit and structured.

Recommended prompt pattern:

1. State the exact goal.
2. State the exact files or subsystem.
3. State constraints and forbidden changes.
4. State required validation.
5. State the required final report format.

Example:

```text
Task: Implement the smallest correct patch to make the gateway load models from configs/inference/models.yaml.
Scope: Only touch services/gateway/*, tests/smoke/test_gateway_basic.py, and docs if needed.
Constraints:
- Keep canonical service paths: services/gateway and services/rag_api.
- Do not use gateway_pkg or rag_api_pkg.
- Do not add unrelated refactors.
Validation:
- python -m repo2ctl.cli lint
- python -m repo2ctl.cli smoke
Final output:
- Include the Review info block from AGENTS.md.
```

## Prompting guidance for `gpt-5.4`

Use `gpt-5.4` when the repo state is unclear or when the task crosses many files.
Ask it to:

- inspect current architecture first
- propose a phased plan
- identify consistency risks
- review validation quality
- decide whether a mini-generated patch is acceptable

## Review info after each run

Codex should end each coding run with:

```text
Review info:
- Branch:
- HEAD commit:
- Commit range:
- Ziel der Änderung:
- Wichtigste geänderte Dateien:
- Ausgeführte Validierung:
- Ergebnis der Validierung:
- Offene Risiken / TODOs:
- Empfohlene nächste Schritte:
```

You can also print a helper scaffold with:

```bash
python -m repo2ctl.cli review-info
```
