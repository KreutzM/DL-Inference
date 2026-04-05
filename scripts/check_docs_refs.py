from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_TO_CHECK = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "docs/architecture/00-system-overview.md",
    REPO_ROOT / "docs/deployment/local-dev.md",
    REPO_ROOT / "docs/development/codex-cli.md",
]
REQUIRED_SNIPPETS = [
    "services/gateway",
    "services/rag_api",
]


def main() -> int:
    errors: list[str] = []
    for path in DOCS_TO_CHECK:
        if not path.exists():
            errors.append(f"Missing required doc: {path.relative_to(REPO_ROOT).as_posix()}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in REQUIRED_SNIPPETS:
            if snippet not in text:
                errors.append(
                    f"Missing required snippet '{snippet}' in {path.relative_to(REPO_ROOT).as_posix()}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Documentation references look consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
