from __future__ import annotations

from pathlib import Path

from repo2ctl import cli


def test_up_dev_uses_mvp_compose_files(monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = True) -> int:
        seen.append(cmd)
        return 0

    monkeypatch.setattr(cli, "run", fake_run)

    rc = cli.cmd_up_dev(object())

    assert rc == 0
    assert seen == [
        [
            "docker",
            "compose",
            "-f",
            "deploy/compose/docker-compose.mvp.yml",
            "-f",
            "deploy/compose/docker-compose.dev.yml",
            "-f",
            "deploy/compose/docker-compose.rag.yml",
            "up",
            "-d",
        ]
    ]


def test_down_uses_mvp_compose_files(monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = True) -> int:
        seen.append(cmd)
        return 0

    monkeypatch.setattr(cli, "run", fake_run)

    rc = cli.cmd_down(object())

    assert rc == 0
    assert seen == [
        [
            "docker",
            "compose",
            "-f",
            "deploy/compose/docker-compose.mvp.yml",
            "-f",
            "deploy/compose/docker-compose.dev.yml",
            "-f",
            "deploy/compose/docker-compose.rag.yml",
            "down",
        ]
    ]


def test_env_example_isolated_mvp_keys() -> None:
    env_text = Path(".env.example").read_text(encoding="utf-8")
    lines = [line.strip() for line in env_text.splitlines() if line.strip()]

    assert "# Gateway / MVP API" in lines
    assert "# Non-MVP / later stacks" in lines
    assert "QDRANT_URL=http://qdrant:6333" in lines

    mvp_section = lines[lines.index("# Gateway / MVP API") : lines.index("# Non-MVP / later stacks")]
    non_mvp_section = lines[lines.index("# Non-MVP / later stacks") :]

    assert any(line.startswith("OPENROUTER_API_KEY=") for line in mvp_section)
    assert any(line.startswith("QDRANT_URL=") for line in mvp_section)
    for forbidden in [
        "LITELLM_MASTER_KEY=",
        "LITELLM_SALT_KEY=",
        "MONGO_URI=",
        "REDIS_URL=",
        "LIBRECHAT_PORT=",
        "OPENWEBUI_PORT=",
        "VLLM_BASE_URL=",
        "SGLANG_BASE_URL=",
    ]:
        assert any(line.startswith(forbidden) for line in non_mvp_section)
        assert not any(line.startswith(forbidden) for line in mvp_section)
