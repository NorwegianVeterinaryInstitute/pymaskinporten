import sys
from types import ModuleType

import pytest

from pymaskinporten import config


class SecretNotFound(Exception):
    """Stands in for botocore's ClientError (ResourceNotFoundException)."""


class FakeSecretsManager:
    """Stands in for a boto3 secretsmanager client, backed by a dict."""

    def __init__(self, secrets: dict[str, dict]):
        self.secrets = secrets
        self.region = None

    def get_secret_value(self, SecretId):
        if SecretId not in self.secrets:
            raise SecretNotFound(f"Secrets Manager can't find the secret {SecretId}")
        return self.secrets[SecretId]


@pytest.fixture
def secretsmanager(monkeypatch, fake_pem):
    client = FakeSecretsManager(
        {
            "PRIVATE-KEY": {"SecretString": fake_pem},
            "MASKINPORTEN-CLIENT-ID": {"SecretString": "client-id"},
            "KID": {"SecretString": "kid123"},
            "SCOPE": {"SecretString": "scope:a"},
        }
    )

    def make_client(service, region_name=None):
        assert service == "secretsmanager"
        client.region = region_name
        return client

    boto3 = ModuleType("boto3")
    boto3.client = make_client  # ty: ignore[unresolved-attribute]
    monkeypatch.setitem(sys.modules, "boto3", boto3)
    return client


@pytest.mark.unit
def test_loads_secrets_with_dashed_names(secretsmanager, fake_pem):
    cfg = config.load_config("aws", region="eu-north-1")

    assert secretsmanager.region == "eu-north-1"
    assert cfg.PRIVATE_KEY == fake_pem.strip()
    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"


@pytest.mark.unit
def test_region_defaults_to_boto3_configuration(secretsmanager):
    config.load_config("aws")

    assert secretsmanager.region is None


@pytest.mark.unit
def test_missing_secret_raises_runtime_error(secretsmanager):
    del secretsmanager.secrets["SCOPE"]

    with pytest.raises(RuntimeError, match="'SCOPE'") as excinfo:
        config.load_config("aws")

    assert isinstance(excinfo.value.__cause__, SecretNotFound)


@pytest.mark.unit
def test_binary_secret_raises_runtime_error(secretsmanager):
    secretsmanager.secrets["KID"] = {"SecretBinary": b"kid123"}

    with pytest.raises(RuntimeError, match="'KID'.*no string value"):
        config.load_config("aws")


@pytest.mark.unit
def test_client_creation_failure_raises_runtime_error(monkeypatch):
    class NoRegionError(Exception):
        pass

    def make_client(service, region_name=None):
        raise NoRegionError("You must specify a region.")

    boto3 = ModuleType("boto3")
    boto3.client = make_client  # ty: ignore[unresolved-attribute]
    monkeypatch.setitem(sys.modules, "boto3", boto3)

    with pytest.raises(RuntimeError, match="client") as excinfo:
        config.load_config("aws")

    assert isinstance(excinfo.value.__cause__, NoRegionError)


@pytest.mark.unit
def test_missing_sdk_raises_install_hint(monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)

    with pytest.raises(RuntimeError, match=r"pymaskinporten\[aws\]"):
        config.load_config("aws")
