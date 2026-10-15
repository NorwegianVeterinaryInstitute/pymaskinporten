import pytest
from pydantic import ValidationError

from pymaskinporten.config import MaskinportenSecrets, load_config
from pymaskinporten.request_token import build_jwt


@pytest.mark.unit
def test_load_config_returns_model(monkeypatch, fake_pem):
    monkeypatch.setenv("PRIVATE_KEY", fake_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    cfg = load_config()

    assert isinstance(cfg, MaskinportenSecrets)
    assert cfg.PRIVATE_KEY == fake_pem.strip()
    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"


@pytest.mark.unit
@pytest.mark.parametrize("blank", ["", "  ", "\n"])
@pytest.mark.parametrize("field", list(MaskinportenSecrets.model_fields))
def test_blank_value_is_rejected(fake_pem, field, blank):
    values = {
        "PRIVATE_KEY": fake_pem,
        "MASKINPORTEN_CLIENT_ID": "client-id",
        "KID": "kid123",
        "SCOPE": "scope:a",
    }
    values[field] = blank

    with pytest.raises(ValidationError, match=field):
        MaskinportenSecrets(**values)


@pytest.mark.unit
def test_surrounding_whitespace_is_stripped(real_private_key_pem):
    cfg = MaskinportenSecrets(
        PRIVATE_KEY=real_private_key_pem + "\n",
        MASKINPORTEN_CLIENT_ID=" client-id\n",
        KID="kid123\n",
        SCOPE=" scope:a ",
    )

    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"
    # The stripped PEM key still signs
    build_jwt(cfg, "https://test.maskinporten.no/")


@pytest.mark.unit
def test_prefix_selects_prefixed_env_vars(monkeypatch, fake_pem):
    monkeypatch.setenv("PROD_PRIVATE_KEY", fake_pem)
    monkeypatch.setenv("PROD_MASKINPORTEN_CLIENT_ID", "prod-client")
    monkeypatch.setenv("PROD_KID", "prod-kid")
    monkeypatch.setenv("PROD_SCOPE", "prod:scope")
    monkeypatch.setenv("KID", "unprefixed-kid")

    cfg = load_config(prefix="PROD_")

    assert cfg.MASKINPORTEN_CLIENT_ID == "prod-client"
    assert cfg.KID == "prod-kid"


@pytest.mark.unit
def test_missing_prefixed_env_var_names_it(monkeypatch, fake_pem):
    for key in ("PRIVATE_KEY", "MASKINPORTEN_CLIENT_ID", "KID", "SCOPE"):
        monkeypatch.setenv(key, "unprefixed")
        monkeypatch.delenv(f"PROD_{key}", raising=False)

    with pytest.raises(RuntimeError, match="PROD_PRIVATE_KEY"):
        load_config(prefix="PROD_")
