# Codex CLI workflow for this repo

This repository is prepared for a two-model Codex workflow:

- **Primary implementation model:** `gpt-5.4-mini`
- **Secondary heavy/review model:** `gpt-5.4`

## Why this split

Use `gpt-5.4-mini` for fast, well-scoped implementation work.

Use `gpt-5.4` for:
- architecture
- planning
- deep debugging
- repo-wide consistency checks
- deciding whether a previous Codex run was actually correct

## Repo-level controls

Repo guidance lives in:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`

## Recommended profiles

- default / `implement` — `gpt-5.4-mini`
- `mini-fast` — very fast low-depth implementation profile
- `plan` — `gpt-5.4` planning profile
- `review` — `gpt-5.4`
- `research` — `gpt-5.4` with live web search

## Recommended custom agents

- `implementer-mini` — small and medium changes
- `explorer-mini` — read-heavy repo exploration
- `planner` — architecture and phased plans
- `reviewer` — correctness, consistency, and validation review

## Prompting guidance for `gpt-5.4-mini`

Keep tasks explicit and structured.

Good pattern:

1. State the exact goal.
2. State the exact files or subsystem.
3. State constraints and forbidden changes.
4. State required validation.
5. Require the Review info block.

Recommended template:

```text
Ziel:
<exact change>

Scope:
- <files or subsystem>

Constraints:
- smallest correct patch
- no unrelated refactors
- inspect current active service tree before editing
- keep docs/tests aligned

Validation:
- python -m repo2ctl.cli lint
- python -m repo2ctl.cli smoke

Final output:
- include the Review info block from AGENTS.md
```

## Prompting guidance for `gpt-5.4`

Use `gpt-5.4` when:
- the repo state is unclear
- the task crosses many files
- the service-path situation matters
- a mini-generated patch needs a serious review

Good asks for `gpt-5.4`:
- inspect architecture first
- propose a phased plan
- identify consistency risks
- review validation quality
- decide whether a mini-generated patch is acceptable

## Subagent usage

Codex does not spawn subagents automatically.
Ask explicitly.

Examples:

```text
Use explorer-mini to map the current request flow before editing.
```

```text
Use planner to propose a 3-phase migration plan.
```

```text
Use explorer-mini and reviewer in parallel, then combine the findings.
```

## Current service-path policy for Codex runs

The repo currently contains multiple service trees for some components.
Before editing:
- inspect which tree is active for the touched subsystem
- avoid creating a third competing path
- only do a path migration when the task explicitly asks for it
- when migrating, migrate code, tests, Dockerfiles, compose files, scripts, and docs together

## Review info after each run

Codex should end each coding run with:

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

You can scaffold the Git fields with:

```bash
python -m repo2ctl.cli review-info --base origin/main
```

Optional helper fields:

```bash
python -m repo2ctl.cli review-info \
  --base origin/main \
  --goal "..." \
  --validation "python -m repo2ctl.cli lint; python -m repo2ctl.cli smoke" \
  --validation-result "passed" \
  --risks "..." \
  --next-steps "..."
```
