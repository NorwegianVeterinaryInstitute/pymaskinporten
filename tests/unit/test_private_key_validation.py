import pytest
from pydantic import ValidationError

from pymaskinporten.config import load_config


@pytest.mark.unit
def test_private_key_not_valid_but_allowed_by_default(monkeypatch, fake_pem):
    # Note: STRICT_KEY_VALIDATION is NOT set
    monkeypatch.setenv("PRIVATE_KEY", fake_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    cfg = load_config()

    # Still accepted because strict validation is OFF by default
    assert cfg.PRIVATE_KEY == fake_pem


@pytest.mark.unit
def test_private_key_invalid_in_strict_mode(monkeypatch, fake_pem):
    monkeypatch.setenv("STRICT_KEY_VALIDATION", "true")
    monkeypatch.setenv("PRIVATE_KEY", fake_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    # Should fail cryptographic decoding
    try:
        load_config()
        assert False, "Expected ValidationError"
    except ValidationError:
        pass
