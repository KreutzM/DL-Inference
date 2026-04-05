from services.gateway.app.routing import list_models


def test_gateway_basic() -> None:
    model_ids = {model["id"] for model in list_models()}
    assert model_ids == {"mvp_openrouter_chat"}
