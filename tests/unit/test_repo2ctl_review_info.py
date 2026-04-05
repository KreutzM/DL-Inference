from __future__ import annotations

from repo2ctl import cli


def test_review_info_prints_extended_git_fields(monkeypatch, capsys) -> None:
    responses = {
        ("git", "rev-parse", "--abbrev-ref", "HEAD"): "feature/codex-prep",
        ("git", "rev-parse", "HEAD"): "abc123",
        (
            "git",
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{upstream}",
        ): "origin/feature/codex-prep",
        ("git", "merge-base", "origin/main", "HEAD"): "base123",
        (
            "git",
            "status",
            "--short",
        ): "M AGENTS.md\nM repo2ctl/cli.py\n?? docs/development/prompt-templates.md",
    }

    def fake_capture(cmd: list[str]) -> str:
        return responses.get(tuple(cmd), "unknown")

    monkeypatch.setattr(cli, "capture", fake_capture)

    rc = cli.main(
        [
            "review-info",
            "--base",
            "origin/main",
            "--goal",
            "Improve Codex repo preparation",
            "--validation",
            "python -m repo2ctl.cli lint; python -m repo2ctl.cli smoke",
            "--validation-result",
            "passed",
            "--risks",
            "unknown",
            "--next-steps",
            "review git diff",
        ]
    )

    assert rc == 0
    out = capsys.readouterr().out
    assert "Review info:" in out
    assert "- Branch: feature/codex-prep" in out
    assert "- HEAD commit: abc123" in out
    assert "- Base branch: origin/main" in out
    assert "- Upstream: origin/feature/codex-prep" in out
    assert "- Commit range: base123..HEAD" in out
    assert "- Working tree: dirty" in out
    assert "- Ziel der Änderung: Improve Codex repo preparation" in out
    assert "AGENTS.md" in out
    assert "repo2ctl/cli.py" in out
    assert "docs/development/prompt-templates.md" in out
    assert "- Ergebnis der Validierung: passed" in out
