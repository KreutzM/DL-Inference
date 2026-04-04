from services.gateway_pkg.app.routing import list_models


def test_gateway_basic():
    assert any(m["id"] == "local-default" for m in list_models())
