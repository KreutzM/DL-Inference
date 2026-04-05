from repo2ctl.cli import build_parser


def test_stack_up_command_is_available() -> None:
    help_text = build_parser().format_help()
    assert "up-dev" in help_text
    assert "smoke" in help_text
    assert "mvp-acceptance" in help_text
