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
