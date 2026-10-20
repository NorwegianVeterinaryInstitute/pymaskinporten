import threading
import time
from unittest.mock import patch

import pytest

from pymaskinporten.client import MaskinportenClient
from pymaskinporten.config import MaskinportenSecrets
from pymaskinporten.request_token import MaskinportenTokenError


@pytest.fixture
def secrets(real_private_key_pem) -> MaskinportenSecrets:
    return MaskinportenSecrets(
        PRIVATE_KEY=real_private_key_pem,
        MASKINPORTEN_CLIENT_ID="client-id",
        KID="kid123",
        SCOPE="scope:a",
    )


@pytest.fixture
def clock():
    """A controllable monotonic clock for the client module."""
    now = [1000.0]
    with patch("pymaskinporten.client.monotonic", side_effect=lambda: now[0]):
        yield now


@pytest.fixture
def mocked_request():
    with patch("pymaskinporten.client.request_maskinporten_token") as request:
        request.side_effect = [("tok1", 120), ("tok2", 120), ("tok3", 120)]
        yield request


@pytest.mark.unit
def test_token_is_reused_until_refresh_margin(secrets, clock, mocked_request):
    client = MaskinportenClient(secrets, refresh_margin=10)

    assert client.get_token() == "tok1"
    clock[0] += 109
    assert client.get_token() == "tok1"
    clock[0] += 1
    assert client.get_token() == "tok2"
    assert mocked_request.call_count == 2


@pytest.mark.unit
def test_lifetime_shorter_than_margin_is_not_cached(secrets, clock, mocked_request):
    mocked_request.side_effect = [("tok1", 5), ("tok2", 5)]
    client = MaskinportenClient(secrets, refresh_margin=10)

    assert client.get_token() == "tok1"
    assert client.get_token() == "tok2"


@pytest.mark.unit
def test_clear_cache_forces_new_token(secrets, clock, mocked_request):
    client = MaskinportenClient(secrets)

    assert client.get_token() == "tok1"
    client.clear_cache()
    assert client.get_token() == "tok2"


@pytest.mark.unit
def test_failed_request_is_not_cached(secrets, clock, mocked_request):
    mocked_request.side_effect = [MaskinportenTokenError("boom"), ("tok1", 120)]
    client = MaskinportenClient(secrets)

    with pytest.raises(MaskinportenTokenError):
        client.get_token()
    assert client.get_token() == "tok1"


@pytest.mark.unit
def test_settings_are_passed_to_request(secrets, mocked_request):
    client = MaskinportenClient(
        secrets,
        "prod",
        token_url="http://localhost:6969/token",
        audience="http://localhost:6969/",
    )

    client.get_token()

    mocked_request.assert_called_once_with(
        "prod",
        config=secrets,
        token_url="http://localhost:6969/token",
        audience="http://localhost:6969/",
    )


@pytest.mark.unit
def test_config_is_loaded_once_when_not_given(secrets, mocked_request):
    with patch("pymaskinporten.client.load_config", return_value=secrets) as load:
        client = MaskinportenClient()
        client.get_token()
        client.clear_cache()
        client.get_token()

    load.assert_called_once_with()
    assert mocked_request.call_args.kwargs["config"] is secrets


@pytest.mark.unit
@pytest.mark.parametrize(
    ("kwargs", "match"),
    [({"api_env": "production"}, "api_env"), ({"refresh_margin": -1}, "refresh")],
)
def test_invalid_settings_raise(secrets, kwargs, match):
    with pytest.raises(ValueError, match=match):
        MaskinportenClient(secrets, **kwargs)


@pytest.mark.unit
def test_concurrent_callers_share_one_request(secrets):
    calls = 0

    def slow_request(*args, **kwargs):
        nonlocal calls
        calls += 1
        time.sleep(0.1)
        return "tok", 120

    client = MaskinportenClient(secrets)
    results = []
    with patch(
        "pymaskinporten.client.request_maskinporten_token", side_effect=slow_request
    ):
        threads = [
            threading.Thread(target=lambda: results.append(client.get_token()))
            for _ in range(8)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    assert results == ["tok"] * 8
    assert calls == 1
