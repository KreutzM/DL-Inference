# AGENTS.md

This repository is developed primarily with **Codex CLI**.

Default implementation model:
- **`gpt-5.4-mini`** for well-scoped implementation work

Escalation / heavy model:
- **`gpt-5.4`** for planning, architecture, ambiguous requirements, deep debugging, and final review

## Primary objective

Improve the repository while preserving these goals:

1. OpenAI-compatible edge API
2. Local inference first
3. Repo-owned RAG logic
4. Config-driven assistants
5. Clear separation between versioned knowledge and runtime data
6. Codex-friendly implementation and review workflow

## Current service-path policy

The repo is in a transitional service-path state.

Current checked-in service trees include:
- `services/gateway/`
- `services/rag_api/`

Rules:
- **Do not create additional parallel service roots.**
- If you touch an existing subsystem, first inspect which tree is currently active for that subsystem in code, Dockerfiles, tests, and docs.
- Do not assume a migration has already completed just because older prompts or docs mention alternate tree names.
- Stay consistent with the currently active tree unless the task explicitly performs a full path migration.
- If you perform a path migration, migrate code, imports, tests, docs, Dockerfiles, compose files, and scripts together in the same change.
- Never leave behind a half-migrated state without documenting it in the final report.

Target architecture still favors repo-owned gateway and repo-owned RAG logic behind a stable OpenAI-compatible edge API.

## Model usage rules

### Default: `gpt-5.4-mini`

Use for:
- scoped implementation tasks
- config edits
- docs updates
- focused tests
- small to medium refactors with clear boundaries

Work style for `gpt-5.4-mini`:
- Be explicit.
- Follow the requested workflow exactly.
- Prefer the smallest correct patch.
- Do not rely on implicit assumptions.
- State conservative assumptions in the final report.
- Do not expand scope on your own.

### Escalate to `gpt-5.4`

Use for:
- architecture planning
- repo-wide consistency reviews
- tricky debugging
- unclear or conflicting requirements
- multi-step design decisions
- validating whether a previous Codex run was actually correct

## Required execution pattern

For any non-trivial task, follow this order:

1. Inspect the relevant files and nearby docs first.
2. Summarize the intended change in 2-6 bullets before editing.
3. Edit the minimum necessary set of files.
4. Update docs when behavior, architecture, paths, or operator workflow change.
5. Run relevant validation.
6. Review your own diff against the task before finishing.
7. End with the required **Review info** block.

## Ambiguity handling

- Do not stop for minor ambiguity if a conservative default is available.
- Prefer the option that preserves architecture, portability, and testability.
- If a decision is irreversible or high-risk, say so clearly.
- Do not invent infrastructure that is not in scope.
- If the repo is in a transitional state, say which assumption you followed.

## Repo conventions

### Code and config

- Keep Python typed where practical.
- Keep service stubs explicit and easy to replace later.
- Keep config files readable and multiline, not compressed into one-liners.
- Avoid hidden behavior.
- Prefer declarative config over hardcoded logic.
- Avoid duplicate implementations of the same responsibility.

### Operator workflow

Prefer the portable Python entrypoint:

```bash
python -m repo2ctl.cli ...
```

Keep PowerShell support aligned with Bash/Linux workflows.
If you add a Bash-oriented workflow, provide the PowerShell-equivalent path or route it through `repo2ctl`.

## Validation

Run what is relevant. Prefer these commands:

```bash
python -m repo2ctl.cli fmt
python -m repo2ctl.cli lint
python -m repo2ctl.cli test
python -m repo2ctl.cli smoke
python -m repo2ctl.cli review-info --base origin/main
```

If a command cannot be run, say exactly why.

## Definition of done

A change is only complete when it includes, where relevant:
- code/config updates
- matching docs updates
- test or smoke coverage updates
- consistent path usage for the touched subsystem
- a clear final review summary

## Required final output

At the end of each coding run, always provide this block exactly once:

```text
Review info:
- Branch:
- HEAD commit:
- Base branch:
- Upstream:
- Commit range:
- Working tree:
- Ziel der Änderung:
- Wichtigste geänderte Dateien:
- Ausgeführte Validierung:
- Ergebnis der Validierung:
- Offene Risiken / TODOs:
- Empfohlene nächste Schritte:
```

Rules for the block:
- Use `unknown` if a value cannot be determined.
- Do not leave fields blank.
- Prefer `python -m repo2ctl.cli review-info --base origin/main ...` to scaffold the Git fields.
- After using the helper, replace placeholder values like `unknown` where you have the information.
