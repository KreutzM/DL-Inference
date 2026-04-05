from fastapi.testclient import TestClient

from services.gateway.app.main import app
from services.gateway.app.routing import list_models


def test_list_models_includes_alias_and_configured_models() -> None:
    model_ids = {model["id"] for model in list_models()}
    assert "local-default" in model_ids
    assert "qwen3_32b_awq" in model_ids
    assert "qwen2_5_72b_instruct_awq" in model_ids


def test_gateway_health_and_models() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["service"] == "gateway"
    response = client.get("/v1/models")
    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "list"
    assert any(item["id"] == "local-default" for item in payload["data"])
