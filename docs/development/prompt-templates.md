# Prompt templates for Codex in this repo

These templates are optimized for the repo workflow in `AGENTS.md`.

## 1. Standard implementation task (`gpt-5.4-mini`)

```text
Task:
Implement the smallest correct patch for <goal>.

Scope:
- touch only <files / subsystem>

Constraints:
- keep service-root changes consistent with the current `services/` layout
- do not create parallel service roots
- no unrelated refactors
- update docs/tests if behavior or workflow changes
- follow `docs/product/mvp-contract.md` for MVP scope decisions

Validation:
- python -m repo2ctl.cli lint
- python -m repo2ctl.cli smoke

Final output:
- include the Review info block from AGENTS.md
```

## 2. Planning task (`gpt-5.4`)

```text
Review the current repo state for <topic>.
First inspect architecture and active code paths.
Then provide:
1. current state
2. target state
3. risks
4. a phased implementation plan
5. recommended validation gates

Do not code yet.
```

## 3. Post-run review (`gpt-5.4`)

```text
Review this Codex run against the task requirements.

Check:
- correctness
- path consistency
- docs/test drift
- placeholders presented as finished work
- validation quality

Report:
- critical issues
- medium issues
- uncertainties
- exact next fixes
```

## 4. Parallel review with subagents

```text
Use explorer-mini and reviewer in parallel.

explorer-mini:
- map the relevant files and request flow

reviewer:
- inspect correctness, consistency, and missing validation

Wait for both, then merge findings into one concise report.
```

## 5. Explicit migration task

Use this only when the task is actually a migration.
The repo uses canonical service roots under `services/`, so do not treat older path names in prompts or docs as active guidance.

```text
Perform a full migration of <subsystem> from <old path> to <new path>.

Required scope:
- code
- imports
- tests
- Dockerfiles
- compose files
- scripts
- docs

Do not leave a half-migrated state.
Run relevant validation and include the Review info block.
```