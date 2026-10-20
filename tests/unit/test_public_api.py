import pytest

import pymaskinporten
from pymaskinporten import client, config, request_token


@pytest.mark.unit
def test_public_api_is_exported_from_package():
    assert (
        pymaskinporten.request_maskinporten_token
        is request_token.request_maskinporten_token
    )
    assert pymaskinporten.MaskinportenClient is client.MaskinportenClient
    assert pymaskinporten.build_jwt is request_token.build_jwt
    assert pymaskinporten.MaskinportenTokenError is request_token.MaskinportenTokenError
    assert pymaskinporten.load_config is config.load_config
    assert pymaskinporten.MaskinportenSecrets is config.MaskinportenSecrets
    assert set(pymaskinporten.__all__) == {
        "MaskinportenClient",
        "request_maskinporten_token",
        "build_jwt",
        "MaskinportenTokenError",
        "load_config",
        "MaskinportenSecrets",
    }
