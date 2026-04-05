from fastapi.testclient import TestClient

from services.rag_api.app.main import app


def test_rag_basic() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["service"] == "rag_api"
