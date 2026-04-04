from pathlib import Path

from repo2ctl.cli import build_parser


REQUIRED_POWERSHELL_FILES = [
    Path('scripts/repo2.ps1'),
    Path('scripts/smoke-test.ps1'),
    Path('scripts/prepare-model-cache.ps1'),
    Path('deploy/scripts/up.ps1'),
    Path('deploy/scripts/down.ps1'),
    Path('deploy/scripts/logs.ps1'),
    Path('deploy/scripts/healthcheck.ps1'),
]


def test_powershell_entrypoints_exist() -> None:
    for rel_path in REQUIRED_POWERSHELL_FILES:
        assert rel_path.exists(), f'Missing PowerShell entrypoint: {rel_path}'


def test_repo2ctl_knows_core_commands() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    assert 'up-dev' in help_text
    assert 'smoke' in help_text
    assert 'down' in help_text
