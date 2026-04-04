from services.gateway_pkg.app.routing import list_models


def test_models_non_empty():
    assert list_models()
