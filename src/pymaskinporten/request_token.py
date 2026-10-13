import uuid
from datetime import UTC, datetime, timedelta

import httpx2 as httpx
from jwt import encode

from pymaskinporten.config import MaskinportenSecrets, load_config


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


def request_maskinporten_token(api_env: str) -> tuple:
    """
    Requests an access token from Maskinporten using API-specific credentials.

    Args:
        api_env (str): The environment of the API (e.g., "prod" or "test").

    Returns:
        tuple: A tuple containing the access token (str) and its expiration time (int).

    Raises:
        MaskinportenTokenError: If the token request fails.

    Examples:
        request_maskinporten_token(api_env = "test")
    """

    if api_env == "test":
        issuer_url = "https://test.maskinporten.no/token"
    else:
        issuer_url = "https://maskinporten.no/token"

    cfg = load_config()

    jwt_assertion = build_jwt(cfg, issuer_url)

    response = httpx.post(
        issuer_url,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_assertion,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data.get("access_token")
        expires_in = response_data.get("expires_in")
        print(
            f"Access token for {cfg.SCOPE} in {api_env} environment fetched successfully."
        )
        return access_token, expires_in
    else:
        raise MaskinportenTokenError(f"Error {response.status_code}: {response.text}")
