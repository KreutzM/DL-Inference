from __future__ import annotations

import os
import py_compile
import subprocess
import sys
import tempfile

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    Path("AGENTS.md"),
    Path(".codex/config.toml"),
    Path(".codex/agents/implementer-mini.toml"),
    Path(".codex/agents/explorer-mini.toml"),
    Path(".codex/agents/planner.toml"),
    Path(".codex/agents/reviewer.toml"),
    Path("docs/development/codex-cli.md"),
    Path("docs/development/prompt-templates.md"),
    Path("repo2ctl/cli.py"),
]

TOML_FILES = [
    Path(".codex/config.toml"),
    Path(".codex/agents/implementer-mini.toml"),
    Path(".codex/agents/explorer-mini.toml"),
    Path(".codex/agents/planner.toml"),
    Path(".codex/agents/reviewer.toml"),
    Path("pyproject.toml"),
]

PYTHON_TREES = ["repo2ctl", "services", "tests", "scripts"]

SERVICE_PATHS_TO_REPORT = [
    Path("services/gateway"),
    Path("services/gateway_pkg"),
    Path("services/rag-api"),
    Path("services/rag_api_pkg"),
]


def check_required_files(errors: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        if not (REPO_ROOT / rel_path).exists():
            errors.append(f"Missing required file: {rel_path.as_posix()}")


def check_toml(errors: list[str]) -> None:
    for rel_path in TOML_FILES:
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            continue
        try:
            tomllib.loads(file_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"Invalid TOML in {rel_path.as_posix()}: {exc}")


def check_python_compile(errors: list[str]) -> None:
    for tree in PYTHON_TREES:
        target = REPO_ROOT / tree
        if not target.exists():
            continue

        for source in target.rglob("*.py"):
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_path = tmp.name
            try:
                py_compile.compile(
                    str(source),
                    cfile=temp_path,
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compilation failed under {tree}/: {exc.msg}")
                break
            finally:
                try:
                    os.remove(temp_path)
                except FileNotFoundError:
                    pass


def check_docs(errors: list[str]) -> None:
    docs_check = subprocess.run(
        [sys.executable, "scripts/check_docs_refs.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if docs_check.returncode != 0:
        errors.append(
            docs_check.stdout.strip()
            or docs_check.stderr.strip()
            or "Doc checks failed"
        )


def report_service_paths() -> list[str]:
    return [
        path.as_posix()
        for path in SERVICE_PATHS_TO_REPORT
        if (REPO_ROOT / path).exists()
    ]


def main() -> int:
    errors: list[str] = []

    check_required_files(errors)
    check_toml(errors)
    check_python_compile(errors)
    check_docs(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    present_paths = report_service_paths()
    if present_paths:
        print("Transition-state service paths present:")
        for path in present_paths:
            print(f"- {path}")

    print("Repo lint checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
