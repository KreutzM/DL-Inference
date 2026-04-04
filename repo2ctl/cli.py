from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_COMPOSE = ["deploy/compose/docker-compose.base.yml"]
DEV_COMPOSE = BASE_COMPOSE + [
    "deploy/compose/docker-compose.dev.yml",
    "deploy/compose/docker-compose.rag.yml",
    "deploy/compose/docker-compose.vllm.yml",
    "deploy/compose/docker-compose.librechat.yml",
]
PROD_COMPOSE = BASE_COMPOSE + [
    "deploy/compose/docker-compose.prod.yml",
    "deploy/compose/docker-compose.rag.yml",
    "deploy/compose/docker-compose.vllm.yml",
    "deploy/compose/docker-compose.librechat.yml",
    "deploy/compose/docker-compose.observability.yml",
]


def _split_cmd(raw: str | None) -> list[str]:
    if not raw:
        return ["docker", "compose"]
    return raw.split()


def compose_cmd(files: list[str]) -> list[str]:
    cmd = _split_cmd(os.environ.get("COMPOSE_CMD"))
    for compose_file in files:
        cmd.extend(["-f", compose_file])
    return cmd


def run(cmd: list[str], check: bool = True) -> int:
    completed = subprocess.run(cmd, cwd=REPO_ROOT)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def cmd_help(_: argparse.Namespace) -> int:
    print("Commands: fmt lint test smoke up-dev up-prod down logs health tree prepare-model-cache backup restore")
    return 0


def cmd_fmt(_: argparse.Namespace) -> int:
    print("TODO: run formatting tools (ruff format / prettier / yamlfix)")
    return 0


def cmd_lint(_: argparse.Namespace) -> int:
    print("TODO: run lint tools (ruff / mypy / yamllint / markdownlint)")
    return 0


def cmd_test(_: argparse.Namespace) -> int:
    return run([sys.executable, "-m", "pytest", "tests", "-q"])


def cmd_smoke(_: argparse.Namespace) -> int:
    return run([sys.executable, "-m", "pytest", "tests/smoke", "-q"])


def cmd_up_dev(_: argparse.Namespace) -> int:
    return run(compose_cmd(DEV_COMPOSE) + ["up", "-d"])


def cmd_up_prod(_: argparse.Namespace) -> int:
    return run(compose_cmd(PROD_COMPOSE) + ["up", "-d"])


def cmd_down(_: argparse.Namespace) -> int:
    return run(compose_cmd(BASE_COMPOSE) + ["down"])


def cmd_logs(args: argparse.Namespace) -> int:
    cmd = compose_cmd(BASE_COMPOSE) + ["logs", "-f"]
    if args.service:
        cmd.append(args.service)
    return run(cmd)


def cmd_health(args: argparse.Namespace) -> int:
    with urlopen(args.url) as response:  # noqa: S310 - local operator helper
        body = response.read().decode("utf-8").strip()
    print(body)
    return 0


def cmd_tree(args: argparse.Namespace) -> int:
    max_depth = args.max_depth
    for path in sorted(REPO_ROOT.rglob("*")):
        rel = path.relative_to(REPO_ROOT)
        if len(rel.parts) > max_depth:
            continue
        suffix = "/" if path.is_dir() else ""
        print(rel.as_posix() + suffix)
    return 0


def cmd_prepare_model_cache(_: argparse.Namespace) -> int:
    (REPO_ROOT / "model-cache").mkdir(exist_ok=True)
    print("Prepared model-cache/")
    return 0


def cmd_backup(_: argparse.Namespace) -> int:
    print("TODO: backup runtime data")
    return 0


def cmd_restore(_: argparse.Namespace) -> int:
    print("TODO: restore runtime data")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repo2ctl", description="Cross-platform operator CLI for Repo 2")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, func) -> None:
        sp = sub.add_parser(name)
        sp.set_defaults(func=func)

    add("help", cmd_help)
    add("fmt", cmd_fmt)
    add("lint", cmd_lint)
    add("test", cmd_test)
    add("smoke", cmd_smoke)
    add("up-dev", cmd_up_dev)
    add("up-prod", cmd_up_prod)
    add("down", cmd_down)
    add("prepare-model-cache", cmd_prepare_model_cache)
    add("backup", cmd_backup)
    add("restore", cmd_restore)

    logs = sub.add_parser("logs")
    logs.add_argument("service", nargs="?")
    logs.set_defaults(func=cmd_logs)

    health = sub.add_parser("health")
    health.add_argument("--url", default="http://localhost:8001/health")
    health.set_defaults(func=cmd_health)

    tree = sub.add_parser("tree")
    tree.add_argument("--max-depth", type=int, default=3)
    tree.set_defaults(func=cmd_tree)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
