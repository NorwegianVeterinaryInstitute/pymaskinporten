import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import httpx2 as httpx
from jwt import encode

from pymaskinporten.config import MaskinportenSecrets, load_config

ApiEnv = Literal["test", "prod"]

ISSUER_URLS: dict[ApiEnv, str] = {
    "test": "https://test.maskinporten.no/token",
    "prod": "https://maskinporten.no/token",
}


class MaskinportenTokenError(Exception):
    """Raised when Maskinporten rejects a token request."""


def build_jwt(cfg: MaskinportenSecrets, issuer_url: str) -> str:
    """
    A helper function to build a JWT assertion for Maskinporten token requests.

    Args:
        cfg: The configuration object containing necessary credentials.
        issuer_url (str): The URL of the token issuer.

    Returns:
        str: The encoded JWT assertion.
    """

    header = {"kid": cfg.KID}
    if not header["kid"]:
        raise ValueError("JWK must include 'kid'.")

    payload = {
        "aud": issuer_url,
        "iss": cfg.MASKINPORTEN_CLIENT_ID,
        "scope": cfg.SCOPE,
        "iat": datetime.now(tz=UTC),
        "exp": datetime.now(tz=UTC) + timedelta(minutes=1),
        "jti": str(uuid.uuid4()),
    }

    jwt_assertion = encode(payload, cfg.PRIVATE_KEY, algorithm="RS256", headers=header)

    return jwt_assertion


def request_maskinporten_token(
    api_env: ApiEnv = "test", config: MaskinportenSecrets | None = None
) -> tuple[str, int]:
    """
    Requests an access token from Maskinporten.

    Args:
        api_env: The Maskinporten environment, "test" or "prod".
        config: The credentials to use. If None, they are read with `load_config()`.

    Returns:
        tuple: The access token (str) and its lifetime in seconds (int).

    Raises:
        ValueError: If `api_env` is not "test" or "prod".
        MaskinportenTokenError: If the token request fails.

    Examples:
        request_maskinporten_token("test")
        request_maskinporten_token("prod", config=load_config("azure", key_vault_uri=uri))
    """

    if api_env not in ISSUER_URLS:
        raise ValueError(f"api_env must be 'test' or 'prod', got {api_env!r}")
    issuer_url = ISSUER_URLS[api_env]

    cfg = config if config is not None else load_config()

    jwt_assertion = build_jwt(cfg, issuer_url)

    try:
        response = httpx.post(
            issuer_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_assertion,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    except httpx.HTTPError as e:
        raise MaskinportenTokenError(f"Request to {issuer_url} failed: {e}") from e

    if response.status_code != 200:
        raise MaskinportenTokenError(f"Error {response.status_code}: {response.text}")

    try:
        response_data = response.json()
        access_token = response_data["access_token"]
        expires_in = response_data["expires_in"]
    except (ValueError, KeyError, TypeError) as e:
        raise MaskinportenTokenError(
            f"Unexpected token response from {issuer_url}"
        ) from e

    if not (
        isinstance(access_token, str) and access_token and isinstance(expires_in, int)
    ):
        raise MaskinportenTokenError(f"Unexpected token response from {issuer_url}")

    print(
        f"Access token for {cfg.SCOPE} in {api_env} environment fetched successfully."
    )
    return access_token, expires_in
