from unittest.mock import patch

import pytest

from pymaskinporten.app import app


@pytest.mark.unit
def test_token_rejects_unknown_env():
    with patch("pymaskinporten.app.request_maskinporten_token") as request_token:
        response = app.test_client().get("/token?env=production")

    assert response.status_code == 400
    request_token.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize("query", ["", "?env="])
def test_token_defaults_to_test_env(query):
    with patch("pymaskinporten.app.request_maskinporten_token") as request_token:
        request_token.return_value = ("tok", 120)
        response = app.test_client().get(f"/token{query}")

    assert response.status_code == 200
    request_token.assert_called_once_with(api_env="test")


@pytest.fixture
def credentials_env(monkeypatch, fake_pem):
    monkeypatch.setenv("PRIVATE_KEY", fake_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")


@pytest.mark.unit
def test_index_shows_invalid_config_instead_of_500(monkeypatch, credentials_env):
    monkeypatch.setenv("KID", "")

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "Configuration error" in response.text
    assert "KID" in response.text


@pytest.mark.unit
def test_index_config_error_does_not_leak_private_key(monkeypatch, credentials_env):
    # Key material pasted without the PEM armor lines, so a truncated repr would show it
    monkeypatch.setenv(
        "PRIVATE_KEY", "MIIBVwIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEAuQ"
    )
    monkeypatch.setenv("STRICT_KEY_VALIDATION", "true")

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "PRIVATE_KEY" in response.text
    assert "MIIBVwIBADAN" not in response.text
