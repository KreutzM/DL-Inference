from services.gateway.app.routing import list_models


def test_models_only_include_mvp_model():
    models = list_models()
    assert [model["id"] for model in models] == ["mvp_openrouter_chat"]
