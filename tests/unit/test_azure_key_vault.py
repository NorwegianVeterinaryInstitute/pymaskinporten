import sys
from types import ModuleType, SimpleNamespace

import pytest

from pymaskinporten import config

# The loader tells ResourceNotFoundError apart from other Azure errors, so use the real
# exception classes; skip when the azure extra isn't installed
azure_exceptions = pytest.importorskip("azure.core.exceptions")
pytest.importorskip("azure.identity")
pytest.importorskip("azure.keyvault.secrets")
ClientAuthenticationError = azure_exceptions.ClientAuthenticationError
HttpResponseError = azure_exceptions.HttpResponseError
ResourceNotFoundError = azure_exceptions.ResourceNotFoundError


VAULT = "https://my-vault.vault.azure.net/"


class FakeSecretClient:
    """Stands in for azure.keyvault.secrets.SecretClient, backed by a dict."""

    def __init__(self, secrets: dict[str, str]):
        self.secrets = secrets
        self.vault_url = None

    def __call__(self, vault_url, credential):
        self.vault_url = vault_url
        return self

    def get_secret(self, name):
        if name not in self.secrets:
            raise ResourceNotFoundError(f"Secret not found: {name}")
        return SimpleNamespace(value=self.secrets[name])


@pytest.fixture
def vault(monkeypatch, fake_pem):
    client = FakeSecretClient(
        {
            "PRIVATE-KEY": fake_pem,
            "MASKINPORTEN-CLIENT-ID": "client-id",
            "KID": "kid123",
            "SCOPE": "scope:a",
        }
    )
    # The loader imports these when it runs, so patch them on the SDK modules
    monkeypatch.setattr("azure.keyvault.secrets.SecretClient", client)
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", lambda: object())
    return client


@pytest.mark.unit
def test_loads_secrets_with_key_vault_names(vault, fake_pem):
    cfg = config.load_config("azure", key_vault_uri=VAULT)

    assert vault.vault_url == VAULT
    assert cfg.PRIVATE_KEY == fake_pem.strip()
    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"


@pytest.mark.unit
def test_missing_secret_raises_runtime_error(vault):
    del vault.secrets["MASKINPORTEN-CLIENT-ID"]

    with pytest.raises(RuntimeError, match="MASKINPORTEN-CLIENT-ID") as excinfo:
        config.load_config("azure", key_vault_uri=VAULT)

    assert isinstance(excinfo.value.__cause__, ResourceNotFoundError)


@pytest.mark.unit
def test_key_vault_uri_is_required():
    with pytest.raises(ValueError, match="key_vault_uri"):
        config.load_config("azure")


@pytest.mark.unit
@pytest.mark.parametrize(
    "error",
    [
        HttpResponseError("Forbidden: caller lacks secrets/get permission"),
        ClientAuthenticationError("DefaultAzureCredential failed to retrieve a token"),
    ],
)
def test_access_failure_raises_runtime_error(vault, monkeypatch, error):
    def failing_get_secret(name):
        raise error

    monkeypatch.setattr(vault, "get_secret", failing_get_secret)

    with pytest.raises(
        RuntimeError, match="Could not read secret 'PRIVATE-KEY'"
    ) as excinfo:
        config.load_config("azure", key_vault_uri=VAULT)

    assert excinfo.value.__cause__ is error


@pytest.mark.unit
def test_prefix_is_prepended(vault):
    vault.secrets = {f"mp-prod-{name}": v for name, v in vault.secrets.items()}

    cfg = config.load_config("azure", key_vault_uri=VAULT, prefix="mp-prod-")

    assert cfg.KID == "kid123"


@pytest.mark.unit
def test_missing_sdk_raises_install_hint(monkeypatch):
    # An empty azure.keyvault package, so importing secrets from it fails
    keyvault = ModuleType("azure.keyvault")
    keyvault.__path__ = []
    monkeypatch.setitem(sys.modules, "azure.keyvault", keyvault)
    monkeypatch.delitem(sys.modules, "azure.keyvault.secrets", raising=False)

    with pytest.raises(RuntimeError, match=r"pymaskinporten\[azure\]"):
        config.load_config("azure", key_vault_uri=VAULT)
