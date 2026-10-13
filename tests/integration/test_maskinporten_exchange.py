from unittest.mock import patch

from pymaskinporten.request_token import request_maskinporten_token


def test_maskinporten_exchange(real_private_key_pem, monkeypatch):
    fake_response = {
        "access_token": "fake-token",
        "expires_in": 120,
    }

    monkeypatch.setenv("PRIVATE_KEY", real_private_key_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    # Patch httpx.post
    with patch("pymaskinporten.request_token.httpx.post") as mocked_post:
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.json.return_value = fake_response

        token, expires = request_maskinporten_token("test")

        assert token == "fake-token"
        assert expires == 120

        # Ensure correct endpoint hit
        mocked_post.assert_called_once()
        url, _kwargs = mocked_post.call_args
        assert "https://test.maskinporten.no/token" in url[0]
