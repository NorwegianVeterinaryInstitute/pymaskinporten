import sys
from types import ModuleType, SimpleNamespace

import pytest

from pymaskinporten import config

PROJECT = "my-project"


class SecretNotFound(Exception):
    """Stands in for google.api_core.exceptions.NotFound."""


class FakeSecretManagerClient:
    """Stands in for SecretManagerServiceClient, backed by a dict of secret names."""

    def __init__(self, secrets: dict[str, str]):
        self.secrets = secrets
        self.paths: list[str] = []

    def access_secret_version(self, name):
        self.paths.append(name)
        project, secret = name.split("/")[1], name.split("/")[3]
        if project != PROJECT or secret not in self.secrets:
            raise SecretNotFound(f"Secret [{name}] not found or has no versions.")
        data = self.secrets[secret].encode("utf-8")
        return SimpleNamespace(payload=SimpleNamespace(data=data))


def install_fake_sdk(monkeypatch, make_client):
    secretmanager = ModuleType("google.cloud.secretmanager")
    secretmanager.SecretManagerServiceClient = make_client  # ty: ignore[unresolved-attribute]
    cloud = ModuleType("google.cloud")
    cloud.secretmanager = secretmanager  # ty: ignore[unresolved-attribute]
    google = ModuleType("google")
    google.cloud = cloud  # ty: ignore[unresolved-attribute]
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.cloud", cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.secretmanager", secretmanager)


@pytest.fixture
def secret_manager(monkeypatch, fake_pem):
    client = FakeSecretManagerClient(
        {
            "PRIVATE-KEY": fake_pem,
            "MASKINPORTEN-CLIENT-ID": "client-id",
            "KID": "kid123",
            "SCOPE": "scope:a",
        }
    )
    install_fake_sdk(monkeypatch, lambda: client)
    return client


@pytest.mark.unit
def test_loads_latest_versions_with_dashed_names(secret_manager, fake_pem):
    cfg = config.load_config("gcp", project_id=PROJECT)

    assert "projects/my-project/secrets/KID/versions/latest" in secret_manager.paths
    assert cfg.PRIVATE_KEY == fake_pem.strip()
    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"


@pytest.mark.unit
def test_prefix_is_prepended(secret_manager):
    secret_manager.secrets = {
        f"mp-prod-{name}": v for name, v in secret_manager.secrets.items()
    }

    cfg = config.load_config("gcp", project_id=PROJECT, prefix="mp-prod-")

    assert cfg.KID == "kid123"


@pytest.mark.unit
def test_missing_secret_raises_runtime_error(secret_manager):
    del secret_manager.secrets["SCOPE"]

    with pytest.raises(RuntimeError, match="'SCOPE'") as excinfo:
        config.load_config("gcp", project_id=PROJECT)

    assert isinstance(excinfo.value.__cause__, SecretNotFound)


@pytest.mark.unit
def test_client_creation_failure_raises_runtime_error(monkeypatch):
    class DefaultCredentialsError(Exception):
        pass

    def make_client():
        raise DefaultCredentialsError("Your default credentials were not found.")

    install_fake_sdk(monkeypatch, make_client)

    with pytest.raises(RuntimeError, match="client") as excinfo:
        config.load_config("gcp", project_id=PROJECT)

    assert isinstance(excinfo.value.__cause__, DefaultCredentialsError)


@pytest.mark.unit
def test_missing_sdk_raises_install_hint(monkeypatch):
    # An empty google.cloud package, so importing secretmanager from it fails
    cloud = ModuleType("google.cloud")
    cloud.__path__ = []
    monkeypatch.setitem(sys.modules, "google", ModuleType("google"))
    monkeypatch.setitem(sys.modules, "google.cloud", cloud)
    monkeypatch.delitem(sys.modules, "google.cloud.secretmanager", raising=False)

    with pytest.raises(RuntimeError, match=r"pymaskinporten\[gcp\]"):
        config.load_config("gcp", project_id=PROJECT)


@pytest.mark.unit
def test_project_id_is_required():
    with pytest.raises(ValueError, match="project_id"):
        config.load_config("gcp")
