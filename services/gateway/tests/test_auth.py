from services.gateway.app.auth import validate_api_key


def test_validate_api_key():
    assert validate_api_key("x") is True
