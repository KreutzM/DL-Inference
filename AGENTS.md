# AGENTS.md

This repository is developed primarily with **Codex CLI**.
The default implementation model is **`gpt-5.4-mini`** for well-scoped work.
Escalate to **`gpt-5.4`** for planning, architecture, deep debugging, ambiguous requirements, large refactors, or heavy review.

## Primary objective

Improve the repository while preserving these architectural goals:

1. **OpenAI-compatible edge API**
2. **Local inference first**
3. **Repo-owned RAG logic**
4. **Config-driven assistants**
5. **Clear separation between versioned knowledge and runtime data**
6. **Codex-friendly implementation and review workflow**

## Canonical service roots

Treat these paths as the single source of truth:

- `services/gateway/`
- `services/rag_api/`

Legacy paths are deprecated and must not be used for new work:

- `services/gateway_pkg/`
- `services/rag_api_pkg/`
- `services/rag-api/`

When changing imports, Dockerfiles, docs, tests, or compose files, always align them to the canonical paths above.

## Model usage rules

### Default: `gpt-5.4-mini`
Use for:
- scoped implementation tasks
- config edits
- docs updates
- focused test additions
- small to medium refactors with clear boundaries

Prompt and work style for `gpt-5.4-mini`:
- Be explicit.
- Follow the requested workflow exactly.
- Prefer the smallest correct patch.
- Do not rely on implicit assumptions.
- State conservative assumptions in the final report.

### Escalate to `gpt-5.4`
Use for:
- architecture planning
- repo-wide consistency reviews
- tricky debugging
- unclear or conflicting requirements
- multi-step design decisions
- reviewing whether a Codex run was actually correct

## Required execution pattern

For any non-trivial task, follow this order:

1. Inspect the relevant files and nearby docs.
2. Summarize the intended change in 2–6 bullets before editing.
3. Edit the minimum necessary set of files.
4. Update docs when behavior, architecture, paths, or operator workflow change.
5. Run relevant validation.
6. End with the required **Review info** block.

## Ambiguity handling

- Do not stop for minor ambiguity if a conservative default is available.
- Prefer the option that preserves architecture, portability, and testability.
- If a decision is irreversible or high-risk, say so clearly in the final report.
- Do not invent infrastructure that is not in scope.

## Repo conventions

### Code and config
- Keep Python typed where practical.
- Keep service stubs explicit and easy to replace later.
- Keep config files readable and multiline, not compressed into one-liners.
- Avoid hidden behavior.
- Prefer declarative config over hardcoded logic.

### Operator workflow
- Prefer the portable Python entrypoint: `python -m repo2ctl.cli ...`
- Keep PowerShell support aligned with Bash/Linux workflows.
- If you add a Bash-oriented workflow, provide the PowerShell-equivalent path or route it through `repo2ctl`.

### Validation
Run what is relevant. Prefer these commands:

```bash
python -m repo2ctl.cli fmt
python -m repo2ctl.cli lint
python -m repo2ctl.cli test
python -m repo2ctl.cli smoke
```

If a command cannot be run, say exactly why in the final report.

## Definition of done

A change is only considered complete when it includes, where relevant:
- code/config updates
- matching docs updates
- test or smoke coverage updates
- consistent canonical path usage
- a clear final review summary

## Required final output

At the end of each coding run, always provide this block exactly once:

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

If Git metadata is unavailable, explicitly say `unknown` instead of omitting the field.
