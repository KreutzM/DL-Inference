from __future__ import annotations

import compileall
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BANNED_PATHS = [
    REPO_ROOT / "services/gateway_pkg",
    REPO_ROOT / "services/rag_api_pkg",
    REPO_ROOT / "services/rag-api",
]
BANNED_SNIPPETS = [
    "services.gateway_pkg",
    "services.rag_api_pkg",
    "services/rag-api",
    "services/gateway_pkg",
    "services/rag_api_pkg",
]
SCAN_EXTENSIONS = {
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".ps1",
    ".sh",
}
SCAN_NAMES = {"Dockerfile", "Makefile"}
SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
EXCLUDED_SCAN_PATHS = {
    Path("scripts/lint_repo.py"),
    Path(".codex/agents/implementer-mini.toml"),
    Path(".codex/agents/planner.toml"),
    Path(".codex/agents/reviewer.toml"),
}
PYTHON_TREES = ["repo2ctl", "services", "tests", "scripts"]


def should_scan(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)
    if rel in EXCLUDED_SCAN_PATHS:
        return False
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    return path.suffix in SCAN_EXTENSIONS or path.name in SCAN_NAMES


def main() -> int:
    errors: list[str] = []

    for path in BANNED_PATHS:
        if path.exists():
            errors.append(
                "Legacy path still present: "
                f"{path.relative_to(REPO_ROOT).as_posix()}"
            )

    for rel_path in [Path(".codex/config.toml"), Path("pyproject.toml")]:
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            errors.append(f"Missing required file: {rel_path.as_posix()}")
            continue
        try:
            tomllib.loads(file_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"Invalid TOML in {rel_path.as_posix()}: {exc}")

    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Non-UTF8 text file: {path.relative_to(REPO_ROOT).as_posix()}")
            continue
        for snippet in BANNED_SNIPPETS:
            if snippet in text:
                errors.append(
                    f"Forbidden legacy reference '{snippet}' in {path.relative_to(REPO_ROOT).as_posix()}"
                )

    for tree in PYTHON_TREES:
        target = REPO_ROOT / tree
        if target.exists() and not compileall.compile_dir(target, quiet=1):
            errors.append(f"Python compilation failed under {tree}/")

    docs_check = subprocess.run(
        [sys.executable, "scripts/check_docs_refs.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if docs_check.returncode != 0:
        errors.append(docs_check.stdout.strip() or docs_check.stderr.strip() or "Doc checks failed")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Repo lint checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
