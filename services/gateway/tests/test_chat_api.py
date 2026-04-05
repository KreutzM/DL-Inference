from fastapi.testclient import TestClient

from services.gateway.app.main import app


def test_gateway_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok", "service": "gateway"}
