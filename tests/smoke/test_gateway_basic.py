from services.gateway.app.routing import list_models


def test_gateway_basic() -> None:
    model_ids = {model["id"] for model in list_models()}
    assert "local-default" in model_ids
    assert "qwen3_32b_awq" in model_ids
