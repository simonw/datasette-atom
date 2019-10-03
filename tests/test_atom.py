from .utils import make_app_client


def test_missing_parameters_produces_400_page():
    app = make_app_client()
    response = app.get("/:memory:.atom?sql=select+sqlite_version()")
    assert 400 == response.status
    assert "text/html; charset=utf-8" == response.headers["content-type"]
