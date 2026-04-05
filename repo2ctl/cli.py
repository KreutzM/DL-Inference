from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent

BASE_COMPOSE = ["deploy/compose/docker-compose.base.yml"]
MVP_COMPOSE = [
    "deploy/compose/docker-compose.mvp.yml",
    "deploy/compose/docker-compose.dev.yml",
    "deploy/compose/docker-compose.rag.yml",
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


def capture(cmd: list[str]) -> str:
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def capture_lines(cmd: list[str]) -> list[str]:
    output = capture(cmd)
    if output == "unknown":
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def cmd_help(_: argparse.Namespace) -> int:
    print(
        "Commands: fmt lint docs test smoke mvp-acceptance up-dev up-prod down logs health tree "
        "prepare-model-cache backup restore review-info"
    )
    return 0


def cmd_fmt(_: argparse.Namespace) -> int:
    return run([sys.executable, "scripts/fmt_repo.py"])


def cmd_lint(_: argparse.Namespace) -> int:
    return run([sys.executable, "scripts/lint_repo.py"])


def cmd_docs(_: argparse.Namespace) -> int:
    return run([sys.executable, "scripts/check_docs_refs.py"])


def cmd_test(_: argparse.Namespace) -> int:
    return run([sys.executable, "-m", "pytest", "tests", "-q"])


def cmd_smoke(_: argparse.Namespace) -> int:
    return run([sys.executable, "-m", "pytest", "tests/smoke", "-q"])


def _request_json(method: str, url: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    response = httpx.request(method, url, json=payload, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise SystemExit(f"Expected JSON object from {url}")
    return data


def _wait_for_health(url: str, label: str, attempts: int = 30, delay_seconds: float = 1.0) -> None:
    last_error: str | None = None
    for _ in range(attempts):
        try:
            payload = _request_json("GET", url)
            if payload.get("status") == "ok":
                return
            last_error = f"{label} health check returned {payload!r}"
        except Exception as exc:  # pragma: no cover - exercised through integration path
            last_error = f"{label} health check failed: {exc}"
        time.sleep(delay_seconds)
    raise SystemExit(last_error or f"{label} health check failed")


def _assert_non_empty(value: object, label: str) -> None:
    if not value:
        raise SystemExit(f"{label} was empty")


def cmd_mvp_acceptance(args: argparse.Namespace) -> int:
    print("Starting MVP stack...")
    cmd_up_dev(args)

    print("Waiting for gateway and RAG health endpoints...")
    _wait_for_health(f"{args.gateway_url.rstrip('/')}/health", "gateway")
    _wait_for_health(f"{args.rag_url.rstrip('/')}/health", "rag_api")

    ingest_payload = {
        "assistant": args.assistant,
        "knowledge_base": args.knowledge_base,
    }
    print("Ingesting MVP knowledge base...")
    ingest = _request_json("POST", f"{args.rag_url.rstrip('/')}/ingest", ingest_payload)
    _assert_non_empty(ingest.get("chunks_indexed"), "ingest.chunks_indexed")

    retrieve_payload = {
        "assistant": args.assistant,
        "knowledge_base": args.knowledge_base,
        "query": args.query,
        "top_k": args.top_k,
    }
    print("Retrieving evidence...")
    retrieval = _request_json("POST", f"{args.rag_url.rstrip('/')}/retrieve", retrieve_payload)
    sources = retrieval.get("sources", [])
    citations = retrieval.get("citations", [])
    if not isinstance(sources, list) or not sources:
        raise SystemExit("RAG retrieval returned no sources")
    if not isinstance(citations, list) or not citations:
        raise SystemExit("RAG retrieval returned no citations")

    chat_payload = {
        "model": args.model,
        "messages": [
            {"role": "user", "content": args.query},
        ],
        "stream": False,
    }
    print("Calling gateway chat completions...")
    completion = _request_json(
        "POST",
        f"{args.gateway_url.rstrip('/')}/v1/chat/completions",
        chat_payload,
    )

    _assert_non_empty(completion.get("choices"), "chat.completion choices")
    _assert_non_empty(completion.get("citations"), "chat.completion citations")
    retrieval_payload = completion.get("retrieval")
    if not isinstance(retrieval_payload, dict):
        raise SystemExit("chat.completion retrieval metadata was missing")
    _assert_non_empty(retrieval_payload.get("sources"), "chat.completion retrieval.sources")

    print(
        "MVP acceptance succeeded: "
        f"ingested {ingest.get('chunks_indexed')} chunks, "
        f"retrieved {len(sources)} sources, "
        f"gateway returned {len(completion.get('citations', []))} citations."
    )
    return 0


def cmd_up_dev(_: argparse.Namespace) -> int:
    return run(compose_cmd(MVP_COMPOSE) + ["up", "-d"])


def cmd_up_prod(_: argparse.Namespace) -> int:
    return run(compose_cmd(PROD_COMPOSE) + ["up", "-d"])


def cmd_down(_: argparse.Namespace) -> int:
    return run(compose_cmd(MVP_COMPOSE) + ["down"])


def cmd_logs(args: argparse.Namespace) -> int:
    cmd = compose_cmd(MVP_COMPOSE) + ["logs", "-f"]
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


def _git_branch() -> str:
    return capture(["git", "rev-parse", "--abbrev-ref", "HEAD"])


def _git_head() -> str:
    return capture(["git", "rev-parse", "HEAD"])


def _git_upstream() -> str:
    return capture(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]
    )


def _git_merge_base(base: str) -> str:
    if not base or base == "unknown":
        return "unknown"
    return capture(["git", "merge-base", base, "HEAD"])


def _git_working_tree() -> str:
    status = capture(["git", "status", "--short"])
    if status == "unknown":
        return "unknown"
    return "clean" if not status else "dirty"


def _git_changed_files(base: str, limit: int) -> list[str]:
    status_lines = capture_lines(["git", "status", "--short"])
    names: list[str] = []

    if status_lines:
        for line in status_lines:
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                names.append(parts[1])

    if not names and base and base != "unknown":
        merge_base = _git_merge_base(base)
        if merge_base != "unknown":
            names = capture_lines(["git", "diff", "--name-only", f"{merge_base}..HEAD"])

    deduped: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name not in seen:
            seen.add(name)
            deduped.append(name)

    return deduped[:limit]


def _commit_range(base: str) -> str:
    if base and base != "unknown":
        merge_base = _git_merge_base(base)
        if merge_base != "unknown":
            return f"{merge_base}..HEAD"
        return f"{base}..HEAD"

    head = _git_head()
    if head == "unknown":
        return "unknown"

    previous = capture(["git", "rev-parse", "HEAD~1"])
    if previous == "unknown":
        return "HEAD"

    return f"{previous}..HEAD"


def _print_list_or_unknown(items: list[str], fallback: str = "unknown") -> None:
    if not items:
        print(f"- Wichtigste geänderte Dateien: {fallback}")
        return

    print("- Wichtigste geänderte Dateien:")
    for item in items:
        print(f"  - {item}")


def cmd_review_info(args: argparse.Namespace) -> int:
    branch = _git_branch()
    head = _git_head()
    upstream = _git_upstream()
    base = args.base or upstream
    if not base:
        base = "unknown"

    changed_files = _git_changed_files(base, args.changed_files_limit)

    print("Review info:")
    print(f"- Branch: {branch}")
    print(f"- HEAD commit: {head}")
    print(f"- Base branch: {base}")
    print(f"- Upstream: {upstream}")
    print(f"- Commit range: {_commit_range(base)}")
    print(f"- Working tree: {_git_working_tree()}")
    print(f"- Ziel der Änderung: {args.goal or 'unknown'}")
    _print_list_or_unknown(changed_files)
    print(f"- Ausgeführte Validierung: {args.validation or 'unknown'}")
    print(f"- Ergebnis der Validierung: {args.validation_result or 'unknown'}")
    print(f"- Offene Risiken / TODOs: {args.risks or 'unknown'}")
    print(f"- Empfohlene nächste Schritte: {args.next_steps or 'unknown'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo2ctl",
        description="Cross-platform operator CLI for Repo 2",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, func) -> None:
        sp = sub.add_parser(name)
        sp.set_defaults(func=func)

    add("help", cmd_help)
    add("fmt", cmd_fmt)
    add("lint", cmd_lint)
    add("docs", cmd_docs)
    add("test", cmd_test)
    add("smoke", cmd_smoke)
    acceptance = sub.add_parser("mvp-acceptance")
    acceptance.add_argument("--gateway-url", default=os.environ.get("GATEWAY_URL", "http://127.0.0.1:4000"))
    acceptance.add_argument("--rag-url", default=os.environ.get("RAG_API_URL", "http://127.0.0.1:8010"))
    acceptance.add_argument("--assistant", default="mvp-openrouter")
    acceptance.add_argument("--knowledge-base", default="mvp-one")
    acceptance.add_argument("--model", default="mvp_openrouter_chat")
    acceptance.add_argument(
        "--query",
        default="How do I reset settings in JAWS?",
    )
    acceptance.add_argument("--top-k", type=int, default=3)
    acceptance.set_defaults(func=cmd_mvp_acceptance)
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

    review_info = sub.add_parser("review-info")
    review_info.add_argument("--base")
    review_info.add_argument("--goal")
    review_info.add_argument("--validation")
    review_info.add_argument("--validation-result")
    review_info.add_argument("--risks")
    review_info.add_argument("--next-steps")
    review_info.add_argument("--changed-files-limit", type=int, default=12)
    review_info.set_defaults(func=cmd_review_info)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
