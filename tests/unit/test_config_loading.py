import pytest

from pymaskinporten.config import MaskinportenSecrets, load_config


@pytest.mark.unit
def test_load_config_returns_model(monkeypatch, fake_pem):
    monkeypatch.setenv("PRIVATE_KEY", fake_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    cfg = load_config()

    assert isinstance(cfg, MaskinportenSecrets)
    assert cfg.PRIVATE_KEY == fake_pem
    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"
