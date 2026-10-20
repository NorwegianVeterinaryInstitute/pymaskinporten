import json
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import httpx2 as httpx
from jwt import encode

from pymaskinporten.config import MaskinportenSecrets, load_config

logger = logging.getLogger(__name__)

ApiEnv = Literal["test", "prod"]

# Maskinporten's issuer identifiers; the JWT `aud` must be one of these, not the
# token endpoint, which Maskinporten no longer accepts as an audience
ISSUER_URLS: dict[ApiEnv, str] = {
    "test": "https://test.maskinporten.no/",
    "prod": "https://maskinporten.no/",
}


class MaskinportenTokenError(Exception):
    """
    Raised when Maskinporten rejects a token request.

    Attributes:
        status: The HTTP status code, or None if no response was received.
        code: The OAuth `error` code, e.g. "invalid_scope", if Maskinporten sent one.
        description: The OAuth `error_description`, or the raw response body when it
            isn't an OAuth error, if there was one.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.description = description


def _error_from_response(response: httpx.Response) -> MaskinportenTokenError:
    """Build the error for a failed token response from its OAuth error body."""
    text = response.text
    code = description = None
    try:
        body = json.loads(text)
    except ValueError:
        body = None
        description = text.strip() or None
    # Maskinporten sends OAuth error bodies (RFC 6749, section 5.2)
    if isinstance(body, dict):
        if isinstance(body.get("error"), str):
            code = body["error"]
        if isinstance(body.get("error_description"), str):
            description = body["error_description"]
    return MaskinportenTokenError(
        f"Error {response.status_code}: {text}",
        status=response.status_code,
        code=code,
        description=description,
    )


def build_jwt(cfg: MaskinportenSecrets, issuer_url: str) -> str:
    """
    A helper function to build a JWT assertion for Maskinporten token requests.

    Args:
        cfg: The configuration object containing necessary credentials.
        issuer_url (str): Maskinporten's issuer identifier, used as the JWT audience,
            e.g. "https://test.maskinporten.no/".

    Returns:
        str: The encoded JWT assertion.
    """

    header = {"kid": cfg.KID}

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
    api_env: ApiEnv = "test",
    config: MaskinportenSecrets | None = None,
    *,
    token_url: str | None = None,
    audience: str | None = None,
) -> tuple[str, int]:
    """
    Requests an access token from Maskinporten.

    Args:
        api_env: The Maskinporten environment, "test" or "prod".
        config: The credentials to use. If None, they are read with `load_config()`.
        token_url: The token endpoint to call, e.g. a local mock. Defaults to the
            `api_env` endpoint, e.g. "https://test.maskinporten.no/token".
        audience: The JWT audience. Defaults to the `api_env` issuer, e.g.
            "https://test.maskinporten.no/".

    Returns:
        tuple: The access token (str) and its lifetime in seconds (int).

    Raises:
        ValueError: If `api_env` is not "test" or "prod".
        MaskinportenTokenError: If the token request fails.

    Examples:
        request_maskinporten_token("test")
        request_maskinporten_token("prod", config=load_config("azure", key_vault_uri=uri))
        request_maskinporten_token(
            token_url="http://localhost:6969/token", audience="http://localhost:6969/"
        )
    """

    token_url, audience = _resolve_endpoints(api_env, token_url, audience)

    cfg = config if config is not None else load_config()

    jwt_assertion = build_jwt(cfg, audience)

    try:
        response = httpx.post(
            token_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_assertion,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    except httpx.HTTPError as e:
        raise MaskinportenTokenError(f"Request to {token_url} failed: {e}") from e

    access_token, expires_in = _parse_token_response(response, token_url)

    logger.info("Fetched Maskinporten access token for %s (%s)", cfg.SCOPE, api_env)
    return access_token, expires_in


def _resolve_endpoints(
    api_env: ApiEnv, token_url: str | None, audience: str | None
) -> tuple[str, str]:
    """Return the token URL and JWT audience, defaulting to those of `api_env`."""
    if api_env not in ISSUER_URLS:
        raise ValueError(f"api_env must be 'test' or 'prod', got {api_env!r}")
    if audience is None:
        audience = ISSUER_URLS[api_env]
    if token_url is None:
        token_url = ISSUER_URLS[api_env] + "token"
    return token_url, audience


def _parse_token_response(response: httpx.Response, token_url: str) -> tuple[str, int]:
    """Return the access token and its lifetime, or raise for a failed response."""
    if response.status_code != 200:
        raise _error_from_response(response)

    try:
        response_data = response.json()
        access_token = response_data["access_token"]
        expires_in = response_data["expires_in"]
    except (ValueError, KeyError, TypeError) as e:
        raise MaskinportenTokenError(
            f"Unexpected token response from {token_url}",
            status=response.status_code,
        ) from e

    if not (
        isinstance(access_token, str) and access_token and isinstance(expires_in, int)
    ):
        raise MaskinportenTokenError(
            f"Unexpected token response from {token_url}",
            status=response.status_code,
        )

    return access_token, expires_in
