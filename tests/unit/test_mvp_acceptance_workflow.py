from __future__ import annotations

from types import SimpleNamespace

from repo2ctl import cli


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


def test_mvp_acceptance_runs_end_to_end(monkeypatch, capsys) -> None:
    seen_runs: list[list[str]] = []
    seen_requests: list[tuple[str, str, dict[str, object] | None]] = []

    def fake_run(cmd: list[str], check: bool = True) -> int:
        seen_runs.append(cmd)
        return 0

    def fake_request(method: str, url: str, json: dict[str, object] | None = None, timeout: float = 30.0) -> FakeResponse:
        seen_requests.append((method, url, json))
        if url.endswith("/health"):
            return FakeResponse({"status": "ok"})
        if url.endswith("/ingest"):
            return FakeResponse(
                {
                    "status": "ok",
                    "assistant": "mvp-openrouter",
                    "knowledge_base": "mvp-one",
                    "collection": "mvp-one",
                    "documents_ingested": 1,
                    "chunks_indexed": 2,
                    "vector_store_path": "knowledge/processed/vector_store/qdrant",
                    "meta": {},
                }
            )
        if url.endswith("/retrieve"):
            return FakeResponse(
                {
                    "status": "ok",
                    "assistant": "mvp-openrouter",
                    "knowledge_base": "mvp-one",
                    "query": "How do I reset settings in JAWS?",
                    "top_k": 3,
                    "sources": [
                        {
                            "source_id": "mvp-one:jaws-support-mvp.md:0",
                            "document_id": "mvp-one:jaws-support-mvp.md",
                            "chunk_id": "mvp-one:jaws-support-mvp.md:0",
                            "score": 0.9,
                            "source": "knowledge/sources/mvp-one/raw/jaws-support-mvp.md",
                            "title": "MVP JAWS Support Knowledge Base",
                            "text": "If a user asks how to reset JAWS settings...",
                            "metadata": {},
                        }
                    ],
                    "citations": [
                        {
                            "citation_id": "cite-1",
                            "source_id": "mvp-one:jaws-support-mvp.md:0",
                            "document_id": "mvp-one:jaws-support-mvp.md",
                            "chunk_id": "mvp-one:jaws-support-mvp.md:0",
                            "source": "knowledge/sources/mvp-one/raw/jaws-support-mvp.md",
                            "score": 0.9,
                        }
                    ],
                    "meta": {},
                }
            )
        if url.endswith("/v1/chat/completions"):
            return FakeResponse(
                {
                    "id": "chatcmpl-test",
                    "object": "chat.completion",
                    "created": 123,
                    "model": "mvp_openrouter_chat",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Reset JAWS settings by renaming the settings folder.",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "citations": [
                        {
                            "citation_id": "cite-1",
                            "source_id": "mvp-one:jaws-support-mvp.md:0",
                            "document_id": "mvp-one:jaws-support-mvp.md",
                            "chunk_id": "mvp-one:jaws-support-mvp.md:0",
                            "source": "knowledge/sources/mvp-one/raw/jaws-support-mvp.md",
                            "score": 0.9,
                        }
                    ],
                    "retrieval": {
                        "assistant": "mvp-openrouter",
                        "knowledge_base": "mvp-one",
                        "sources": [
                            {
                                "source_id": "mvp-one:jaws-support-mvp.md:0",
                                "document_id": "mvp-one:jaws-support-mvp.md",
                                "chunk_id": "mvp-one:jaws-support-mvp.md:0",
                                "score": 0.9,
                                "source": "knowledge/sources/mvp-one/raw/jaws-support-mvp.md",
                                "title": "MVP JAWS Support Knowledge Base",
                                "text": "If a user asks how to reset JAWS settings...",
                                "metadata": {},
                            }
                        ],
                        "meta": {},
                    },
                }
            )
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(cli, "run", fake_run)
    monkeypatch.setattr(cli.httpx, "request", fake_request)

    rc = cli.cmd_mvp_acceptance(
        SimpleNamespace(
            gateway_url="http://127.0.0.1:4000",
            rag_url="http://127.0.0.1:8010",
            assistant="mvp-openrouter",
            knowledge_base="mvp-one",
            model="mvp_openrouter_chat",
            query="How do I reset settings in JAWS?",
            top_k=3,
        )
    )

    assert rc == 0
    assert seen_runs == [["docker", "compose", "-f", "deploy/compose/docker-compose.mvp.yml", "-f", "deploy/compose/docker-compose.dev.yml", "-f", "deploy/compose/docker-compose.rag.yml", "up", "-d"]]
    assert [item[0] for item in seen_requests] == ["GET", "GET", "POST", "POST", "POST"]
    out = capsys.readouterr().out
    assert "MVP acceptance succeeded" in out
