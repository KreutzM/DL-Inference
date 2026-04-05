from services.gateway_pkg.app.main import app


def test_app_exists():
    assert app.title == "Repo2 Gateway"
