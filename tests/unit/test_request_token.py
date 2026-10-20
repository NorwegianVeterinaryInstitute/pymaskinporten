import logging
from unittest.mock import patch

import httpx2 as httpx
import jwt
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
    ("api_env", "issuer"),
    [
        ("test", "https://test.maskinporten.no/"),
        ("prod", "https://maskinporten.no/"),
    ],
)
def test_api_env_selects_issuer(secrets, mocked_post, api_env, issuer):
    request_maskinporten_token(api_env, config=secrets)

    assert mocked_post.call_args.args[0] == issuer + "token"
    assertion = mocked_post.call_args.kwargs["data"]["assertion"]
    claims = jwt.decode(assertion, options={"verify_signature": False})
    assert claims["aud"] == issuer


@pytest.mark.unit
@pytest.mark.parametrize(
    ("overrides", "url", "aud"),
    [
        (
            {"token_url": "http://localhost:6969/token"},
            "http://localhost:6969/token",
            "https://test.maskinporten.no/",
        ),
        (
            {"audience": "http://localhost:6969/"},
            "https://test.maskinporten.no/token",
            "http://localhost:6969/",
        ),
        (
            {
                "token_url": "http://localhost:6969/token",
                "audience": "http://localhost:6969/",
            },
            "http://localhost:6969/token",
            "http://localhost:6969/",
        ),
    ],
)
def test_overrides_replace_env_defaults(secrets, mocked_post, overrides, url, aud):
    request_maskinporten_token("test", config=secrets, **overrides)

    assert mocked_post.call_args.args[0] == url
    assertion = mocked_post.call_args.kwargs["data"]["assertion"]
    claims = jwt.decode(assertion, options={"verify_signature": False})
    assert claims["aud"] == aud


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
@pytest.mark.parametrize(
    ("text", "code", "description"),
    [
        (
            '{"error":"invalid_scope","error_description":"Scope not allowed"}',
            "invalid_scope",
            "Scope not allowed",
        ),
        ('{"error":"invalid_client"}', "invalid_client", None),
        ('{"error":42,"error_description":["x"]}', None, None),
        ('["not", "an", "object"]', None, None),
        ("Bad Gateway\n", None, "Bad Gateway"),
        ("", None, None),
    ],
)
def test_non_200_error_fields(secrets, mocked_post, text, code, description):
    mocked_post.return_value.status_code = 400
    mocked_post.return_value.text = text

    with pytest.raises(MaskinportenTokenError) as excinfo:
        request_maskinporten_token("test", config=secrets)

    error = excinfo.value
    assert (error.status, error.code, error.description) == (400, code, description)
    assert str(error) == f"Error 400: {text}"


@pytest.mark.unit
def test_network_error_raises_token_error(secrets, mocked_post):
    mocked_post.side_effect = httpx.ConnectError("connection refused")

    with pytest.raises(MaskinportenTokenError) as excinfo:
        request_maskinporten_token("test", config=secrets)

    assert isinstance(excinfo.value.__cause__, httpx.ConnectError)
    error = excinfo.value
    assert (error.status, error.code, error.description) == (None, None, None)


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

    with pytest.raises(MaskinportenTokenError, match="Unexpected token response") as e:
        request_maskinporten_token("test", config=secrets)

    assert e.value.status == 200


@pytest.mark.unit
def test_200_with_non_json_body_raises_token_error(secrets, mocked_post):
    mocked_post.return_value.json.side_effect = ValueError("not JSON")

    with pytest.raises(MaskinportenTokenError, match="Unexpected token response"):
        request_maskinporten_token("test", config=secrets)


@pytest.mark.unit
def test_success_is_logged_not_printed(secrets, mocked_post, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="pymaskinporten.request_token"):
        request_maskinporten_token("test", config=secrets)

    assert "scope:a" in caplog.text
    assert capsys.readouterr().out == ""
