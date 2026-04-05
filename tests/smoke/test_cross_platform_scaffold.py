from pathlib import Path

from repo2ctl.cli import build_parser

REQUIRED_POWERSHELL_FILES = [
    Path("scripts/repo2.ps1"),
    Path("scripts/smoke-test.ps1"),
    Path("scripts/prepare-model-cache.ps1"),
    Path("deploy/scripts/up.ps1"),
    Path("deploy/scripts/down.ps1"),
    Path("deploy/scripts/logs.ps1"),
    Path("deploy/scripts/healthcheck.ps1"),
]
REQUIRED_CODEX_FILES = [
    Path("AGENTS.md"),
    Path(".codex/config.toml"),
    Path(".codex/agents/implementer-mini.toml"),
    Path(".codex/agents/planner.toml"),
    Path(".codex/agents/reviewer.toml"),
]
REQUIRED_ACTIVE_SERVICE_DIRS = [
    Path("services/gateway"),
    Path("services/rag_api"),
]


def test_powershell_entrypoints_exist() -> None:
    for rel_path in REQUIRED_POWERSHELL_FILES:
        assert rel_path.exists(), f"Missing PowerShell entrypoint: {rel_path}"



def test_codex_repo_controls_exist() -> None:
    for rel_path in REQUIRED_CODEX_FILES:
        assert rel_path.exists(), f"Missing Codex repo control file: {rel_path}"



def test_transition_service_dirs_exist() -> None:
    for rel_path in REQUIRED_ACTIVE_SERVICE_DIRS:
        assert rel_path.exists(), f"Missing active service dir: {rel_path}"



def test_repo2ctl_knows_core_commands() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    assert "up-dev" in help_text
    assert "smoke" in help_text
    assert "down" in help_text
    assert "review-info" in help_text
