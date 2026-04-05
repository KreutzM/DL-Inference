from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codex_files_exist() -> None:
    required = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".codex" / "config.toml",
        REPO_ROOT / ".codex" / "agents" / "implementer-mini.toml",
        REPO_ROOT / ".codex" / "agents" / "explorer-mini.toml",
        REPO_ROOT / ".codex" / "agents" / "planner.toml",
        REPO_ROOT / ".codex" / "agents" / "reviewer.toml",
        REPO_ROOT / "docs" / "development" / "codex-cli.md",
        REPO_ROOT / "docs" / "development" / "prompt-templates.md",
    ]
    missing = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in required
        if not path.exists()
    ]
    assert not missing, f"Missing Codex prep files: {missing}"
