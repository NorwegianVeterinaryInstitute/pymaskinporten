import threading
from time import monotonic

from pymaskinporten.config import MaskinportenSecrets, load_config
from pymaskinporten.request_token import (
    ApiEnv,
    _resolve_endpoints,
    request_maskinporten_token,
)


class MaskinportenClient:
    """
    Requests Maskinporten access tokens and reuses each one until shortly before it
    expires.

    The client is thread-safe: when the cached token has expired, one thread fetches a
    new token and the others wait for it instead of sending their own requests.

    Args:
        config: The credentials to use. If None, they are read once with
            `load_config()` when the client is created.
        api_env: The Maskinporten environment, "test" or "prod".
        refresh_margin: Seconds before the token expires at which to fetch a new one.
        token_url: The token endpoint to call. Defaults to the `api_env` endpoint.
        audience: The JWT audience. Defaults to the `api_env` issuer.

    Raises:
        ValueError: If `api_env` is not "test" or "prod", or `refresh_margin` is
            negative.

    Examples:
        client = MaskinportenClient(api_env="prod")
        headers = {"Authorization": f"Bearer {client.get_token()}"}
    """

    def __init__(
        self,
        config: MaskinportenSecrets | None = None,
        api_env: ApiEnv = "test",
        *,
        refresh_margin: float = 10,
        token_url: str | None = None,
        audience: str | None = None,
    ) -> None:
        if refresh_margin < 0:
            raise ValueError(f"refresh_margin must be >= 0, got {refresh_margin!r}")
        self._token_url, self._audience = _resolve_endpoints(
            api_env, token_url, audience
        )
        self._config = config if config is not None else load_config()
        self._api_env: ApiEnv = api_env
        self._refresh_margin = refresh_margin
        self._lock = threading.Lock()
        self._token: str | None = None
        self._expires_at = 0.0

    def get_token(self) -> str:
        """
        Returns a valid access token, fetching a new one if the cached one is missing
        or about to expire.

        Raises:
            MaskinportenTokenError: If a new token is needed and the request fails.
        """
        with self._lock:
            if self._token is None or monotonic() >= self._expires_at:
                # Count the lifetime from before the request, so network time can
                # only make the cached token expire early, never late
                requested_at = monotonic()
                token, expires_in = request_maskinporten_token(
                    self._api_env,
                    config=self._config,
                    token_url=self._token_url,
                    audience=self._audience,
                )
                self._token = token
                self._expires_at = requested_at + max(
                    0, expires_in - self._refresh_margin
                )
            return self._token

    def clear_cache(self) -> None:
        """Drops the cached token, so the next `get_token()` fetches a new one."""
        with self._lock:
            self._token = None
            self._expires_at = 0.0
