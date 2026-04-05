from __future__ import annotations

from scripts import lint_repo


def test_lint_repo_reports_transition_state_paths(monkeypatch, capsys) -> None:
    monkeypatch.setattr(lint_repo, "check_required_files", lambda errors: None)
    monkeypatch.setattr(lint_repo, "check_toml", lambda errors: None)
    monkeypatch.setattr(lint_repo, "check_python_compile", lambda errors: None)
    monkeypatch.setattr(lint_repo, "check_docs", lambda errors: None)
    monkeypatch.setattr(
        lint_repo,
        "report_service_paths",
        lambda: [
            "services/gateway",
            "services/gateway_pkg",
            "services/rag-api",
            "services/rag_api_pkg",
        ],
    )

    rc = lint_repo.main()

    assert rc == 0
    out = capsys.readouterr().out
    assert "Transition-state service paths present:" in out
    assert "- services/gateway" in out
    assert "Repo lint checks passed." in out
