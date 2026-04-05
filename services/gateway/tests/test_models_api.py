from services.gateway.app.routing import list_models


def test_models_only_include_mvp_model():
    models = list_models()
    assert [model["id"] for model in models] == ["mvp_openrouter_chat"]
    assert models[0]["metadata"]["provider_model_id"] == "openai/gpt-4o-mini"
