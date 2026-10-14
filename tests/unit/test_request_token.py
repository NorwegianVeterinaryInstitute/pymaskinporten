from unittest.mock import patch

import httpx2 as httpx
import pytest

from pymaskinporten.config import MaskinportenSecrets
from pymaskinporten.request_token import (
    MaskinportenTokenError,
    request_maskinporten_token,
)


@pytest.fixture
def secrets(real_private_key_pem) -> MaskinportenSecrets:
    return MaskinportenSecrets(
        PRIVATE_KEY=real_private_key_pem,
        MASKINPORTEN_CLIENT_ID="client-id",
        KID="kid123",
        SCOPE="scope:a",
    )


@pytest.fixture
def mocked_post():
    with patch("pymaskinporten.request_token.httpx.post") as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"access_token": "tok", "expires_in": 120}
        yield post


@pytest.mark.unit
@pytest.mark.parametrize(
    ("api_env", "url"),
    [
        ("test", "https://test.maskinporten.no/token"),
        ("prod", "https://maskinporten.no/token"),
    ],
)
def test_api_env_selects_issuer(secrets, mocked_post, api_env, url):
    request_maskinporten_token(api_env, config=secrets)

    assert mocked_post.call_args.args[0] == url


@pytest.mark.unit
@pytest.mark.parametrize("api_env", ["production", "Test", ""])
def test_invalid_api_env_raises(secrets, mocked_post, api_env):
    with pytest.raises(ValueError, match="api_env"):
        request_maskinporten_token(api_env, config=secrets)

    mocked_post.assert_not_called()


@pytest.mark.unit
def test_passed_config_is_used_instead_of_env(monkeypatch, secrets, mocked_post):
    for key in MaskinportenSecrets.model_fields:
        monkeypatch.delenv(key, raising=False)

    with patch("pymaskinporten.request_token.load_config") as load_config:
        token, expires = request_maskinporten_token("test", config=secrets)

    load_config.assert_not_called()
    assert (token, expires) == ("tok", 120)


@pytest.mark.unit
def test_non_200_raises_token_error(secrets, mocked_post):
    mocked_post.return_value.status_code = 400
    mocked_post.return_value.text = '{"error":"invalid_grant"}'

    with pytest.raises(MaskinportenTokenError, match="400"):
        request_maskinporten_token("test", config=secrets)


@pytest.mark.unit
def test_network_error_raises_token_error(secrets, mocked_post):
    mocked_post.side_effect = httpx.ConnectError("connection refused")

    with pytest.raises(MaskinportenTokenError) as excinfo:
        request_maskinporten_token("test", config=secrets)

    assert isinstance(excinfo.value.__cause__, httpx.ConnectError)


@pytest.mark.unit
@pytest.mark.parametrize(
    "body",
    [
        {"expires_in": 120},
        {"access_token": "tok"},
        {"access_token": None, "expires_in": 120},
        {"access_token": "", "expires_in": 120},
        {"access_token": "tok", "expires_in": None},
        {"access_token": "tok", "expires_in": "120"},
        [],
        "not a dict",
    ],
)
def test_200_without_token_fields_raises_token_error(secrets, mocked_post, body):
    mocked_post.return_value.json.return_value = body

    with pytest.raises(MaskinportenTokenError, match="Unexpected token response"):
        request_maskinporten_token("test", config=secrets)


@pytest.mark.unit
def test_200_with_non_json_body_raises_token_error(secrets, mocked_post):
    mocked_post.return_value.json.side_effect = ValueError("not JSON")

    with pytest.raises(MaskinportenTokenError, match="Unexpected token response"):
        request_maskinporten_token("test", config=secrets)
