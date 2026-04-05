from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
    ".ps1",
    ".sh",
}
TEXT_NAMES = {"Dockerfile", "Makefile", "AGENTS.md"}
SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__"}


def should_format(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    return path.suffix in TEXT_EXTENSIONS or path.name in TEXT_NAMES


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    changed = 0
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or not should_format(path):
            continue
        original = path.read_text(encoding="utf-8")
        formatted = normalize(original)
        if formatted != original:
            path.write_text(formatted, encoding="utf-8")
            changed += 1
            print(f"formatted: {path.relative_to(REPO_ROOT).as_posix()}")
    print(f"Formatting complete. Files changed: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
