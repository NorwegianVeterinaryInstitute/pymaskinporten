import sys
from types import ModuleType, SimpleNamespace

import pytest

from pymaskinporten import config

SCOPE_NAME = "maskinporten"


class FakeSecrets:
    """Stands in for dbutils.secrets, backed by a dict keyed by (scope, key)."""

    def __init__(self, secrets: dict[tuple[str, str], str]):
        self.secrets = secrets

    def get(self, scope, key):
        if (scope, key) not in self.secrets:
            raise ValueError(
                f"Secret does not exist with scope: {scope} and key: {key}"
            )
        return self.secrets[(scope, key)]


@pytest.fixture
def dbutils(monkeypatch, fake_pem):
    secrets = FakeSecrets(
        {
            (SCOPE_NAME, "PRIVATE-KEY"): fake_pem,
            (SCOPE_NAME, "MASKINPORTEN-CLIENT-ID"): "client-id",
            (SCOPE_NAME, "KID"): "kid123",
            (SCOPE_NAME, "SCOPE"): "scope:a",
        }
    )
    runtime = ModuleType("databricks.sdk.runtime")
    runtime.dbutils = SimpleNamespace(secrets=secrets)  # ty: ignore[unresolved-attribute]
    monkeypatch.setitem(sys.modules, "databricks", ModuleType("databricks"))
    monkeypatch.setitem(sys.modules, "databricks.sdk", ModuleType("databricks.sdk"))
    monkeypatch.setitem(sys.modules, "databricks.sdk.runtime", runtime)
    return secrets


@pytest.mark.unit
def test_loads_secrets_with_dashed_names(dbutils, fake_pem):
    cfg = config.load_config("databricks", secret_scope=SCOPE_NAME)

    assert cfg.PRIVATE_KEY == fake_pem.strip()
    assert cfg.MASKINPORTEN_CLIENT_ID == "client-id"
    assert cfg.KID == "kid123"
    assert cfg.SCOPE == "scope:a"


@pytest.mark.unit
def test_missing_secret_raises_runtime_error(dbutils):
    del dbutils.secrets[(SCOPE_NAME, "KID")]

    with pytest.raises(RuntimeError, match="'KID'") as excinfo:
        config.load_config("databricks", secret_scope=SCOPE_NAME)

    assert isinstance(excinfo.value.__cause__, ValueError)


@pytest.mark.unit
def test_missing_sdk_raises_install_hint(monkeypatch):
    # A None entry in sys.modules makes the import fail, as if the package were missing
    monkeypatch.setitem(sys.modules, "databricks.sdk.runtime", None)

    with pytest.raises(RuntimeError, match="databricks-sdk"):
        config.load_config("databricks", secret_scope=SCOPE_NAME)


@pytest.mark.unit
def test_secret_scope_is_required():
    with pytest.raises(ValueError, match="secret_scope"):
        config.load_config("databricks")


@pytest.mark.unit
def test_prefix_is_prepended(dbutils):
    dbutils.secrets = {
        (scope, f"mp-prod-{name}"): v for (scope, name), v in dbutils.secrets.items()
    }

    cfg = config.load_config("databricks", secret_scope=SCOPE_NAME, prefix="mp-prod-")

    assert cfg.KID == "kid123"
