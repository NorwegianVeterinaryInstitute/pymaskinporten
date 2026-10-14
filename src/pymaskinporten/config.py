import os

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MaskinportenSecrets(BaseModel):
    # Secrets copied from files or secret stores often carry a trailing newline
    model_config = ConfigDict(str_strip_whitespace=True)

    PRIVATE_KEY: str = Field(
        ..., min_length=1, description="PEM string or file contents"
    )
    MASKINPORTEN_CLIENT_ID: str = Field(
        ..., min_length=1, description="Client ID used for Maskinporten"
    )
    KID: str = Field(..., min_length=1, description="Key ID used in JWT header")
    SCOPE: str = Field(..., min_length=1, description="Space-delimited scopes")

    @field_validator("PRIVATE_KEY")
    def validate_private_key(cls, v: str) -> str:
        # Skip strict validation unless explicitly enabled
        if os.getenv("STRICT_KEY_VALIDATION", "").lower() not in {"1", "true", "yes"}:
            return v

        # If strict validation enabled then parse PEM
        try:
            load_pem_private_key(v.encode(), password=None)
        except Exception as exc:
            raise ValueError(f"Invalid PRIVATE_KEY PEM: {exc}") from exc

        return v


def load_config(
    deployment: str = "local",
    secret_scope: str | None = None,
    key_vault_uri: str | None = None,
) -> MaskinportenSecrets:
    if deployment == "local":
        raw = _load_local_env()

    elif deployment == "databricks":
        if not secret_scope:
            raise ValueError("secret_scope is required for Databricks")
        raw = _load_databricks_secrets(secret_scope)

    elif deployment == "azure":
        if not key_vault_uri:
            raise ValueError("key_vault_uri is required for Azure Key Vault")
        raw = _load_azure_key_vault_secrets(key_vault_uri)

    else:
        raise ValueError(f"Unknown deployment type: {deployment}")

    return MaskinportenSecrets(**raw)


def _load_local_env() -> dict[str, str]:
    """Load secret config from environment variables."""
    config: dict[str, str] = {}

    for key in MaskinportenSecrets.model_fields:
        value = os.getenv(key)
        if value is None:
            raise RuntimeError(f"Missing required environment variable: {key}")
        config[key] = value

    return config


def _load_databricks_secrets(secret_scope: str) -> dict[str, str]:
    """Load secret config from Databricks Secrets."""
    config: dict[str, str] = {}

    for key in MaskinportenSecrets.model_fields:
        value = dbutils.secrets.get(scope=secret_scope, key=key)  # noqa: F821 # type: ignore
        if value is None:
            raise RuntimeError(f"Missing required secret in Key Vault: {key}")
        config[key] = value

    return config


def _key_vault_name(field: str) -> str:
    """Key Vault secret name for a config field; Key Vault allows only [0-9a-zA-Z-]."""
    return field.replace("_", "-")


def _load_azure_key_vault_secrets(key_vault_uri: str) -> dict[str, str]:
    """Load secret config from Azure Key Vault."""
    config: dict[str, str] = {}

    # Authenticate using DefaultAzureCredential (Azure Managed Identity or Environment Auth)
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)

    for key in MaskinportenSecrets.model_fields:
        name = _key_vault_name(key)
        try:
            value = client.get_secret(name).value
        except ResourceNotFoundError as e:
            raise RuntimeError(f"Missing required secret in Key Vault: {name}") from e
        if value is None:
            raise RuntimeError(f"Missing required secret in Key Vault: {name}")
        config[key] = value

    return config
