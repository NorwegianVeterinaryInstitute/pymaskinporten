import os

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
    region: str | None = None,
    project_id: str | None = None,
    prefix: str = "",
) -> MaskinportenSecrets:
    """
    Loads and validates Maskinporten credentials.

    Args:
        deployment: Where to read the credentials from:
            "local" reads the environment variables PRIVATE_KEY, MASKINPORTEN_CLIENT_ID, KID
            and SCOPE.
            "azure" reads the Key Vault secrets PRIVATE-KEY, MASKINPORTEN-CLIENT-ID, KID and
            SCOPE, signing in with DefaultAzureCredential; needs pymaskinporten[azure].
            "databricks" reads the same dashed secret names from a Databricks secret scope;
            needs the databricks-sdk package.
            "aws" reads the same dashed secret names from AWS Secrets Manager, signing in
            with boto3's default credential chain; needs pymaskinporten[aws].
            "gcp" reads the same dashed secret names (latest version) from Google Secret
            Manager, signing in with Application Default Credentials; needs
            pymaskinporten[gcp].
        secret_scope: The Databricks secret scope. Required for "databricks".
        key_vault_uri: The Key Vault URL. Required for "azure".
        region: The AWS region for "aws". Defaults to boto3's configured region.
        project_id: The Google Cloud project ID. Required for "gcp".
        prefix: Prepended as-is to every environment variable or secret name, e.g.
            "PROD_" for "local" (reads PROD_KID), "maskinporten/prod/" for AWS or
            "maskinporten-prod-" for Key Vault. Use characters the source allows.

    Returns:
        MaskinportenSecrets: The validated credentials.

    Raises:
        ValueError: If `deployment` is unknown or its required argument is missing.
        RuntimeError: If a credential is missing or can't be read.
        pydantic.ValidationError: If a credential is blank or invalid.

    Examples:
        load_config()
        load_config("azure", key_vault_uri="https://my-vault.vault.azure.net/")
        load_config("databricks", secret_scope="maskinporten")
        load_config("aws", region="eu-north-1", prefix="maskinporten/prod/")
        load_config("gcp", project_id="my-project", prefix="maskinporten-prod-")
    """
    if deployment == "local":
        raw = _load_local_env(prefix)

    elif deployment == "databricks":
        if not secret_scope:
            raise ValueError("secret_scope is required for Databricks")
        raw = _load_databricks_secrets(secret_scope, prefix)

    elif deployment == "azure":
        if not key_vault_uri:
            raise ValueError("key_vault_uri is required for Azure Key Vault")
        raw = _load_azure_key_vault_secrets(key_vault_uri, prefix)

    elif deployment == "aws":
        raw = _load_aws_secrets(region, prefix)

    elif deployment == "gcp":
        if not project_id:
            raise ValueError("project_id is required for Google Secret Manager")
        raw = _load_gcp_secrets(project_id, prefix)

    else:
        raise ValueError(f"Unknown deployment type: {deployment}")

    return MaskinportenSecrets(**raw)


def _load_local_env(prefix: str) -> dict[str, str]:
    """Load secret config from environment variables."""
    config: dict[str, str] = {}

    for key in MaskinportenSecrets.model_fields:
        name = prefix + key
        value = os.getenv(name)
        if value is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        config[key] = value

    return config


def _secret_name(field: str, prefix: str) -> str:
    """Name of a config field in a secret store; Key Vault allows only [0-9a-zA-Z-]."""
    return prefix + field.replace("_", "-")


def _load_databricks_secrets(secret_scope: str, prefix: str) -> dict[str, str]:
    """Load secret config from Databricks Secrets."""
    try:
        from databricks.sdk.runtime import dbutils  # ty: ignore[unresolved-import]
    except ImportError as e:
        raise RuntimeError(
            "Databricks secrets need the databricks-sdk package: pip install databricks-sdk"
        ) from e

    config: dict[str, str] = {}

    for key in MaskinportenSecrets.model_fields:
        name = _secret_name(key, prefix)
        try:
            value = dbutils.secrets.get(scope=secret_scope, key=name)
        except Exception as e:
            # The error type differs between notebooks and the SDK's remote client
            raise RuntimeError(
                f"Could not read secret {name!r} from Databricks scope {secret_scope!r}"
            ) from e
        config[key] = value

    return config


def _load_azure_key_vault_secrets(key_vault_uri: str, prefix: str) -> dict[str, str]:
    """Load secret config from Azure Key Vault."""
    try:
        from azure.core.exceptions import AzureError, ResourceNotFoundError
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
    except ImportError as e:
        raise RuntimeError(
            "Azure Key Vault needs the Azure SDK: pip install pymaskinporten[azure]"
        ) from e

    config: dict[str, str] = {}

    # Authenticate using DefaultAzureCredential (Azure Managed Identity or Environment Auth)
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)

    for key in MaskinportenSecrets.model_fields:
        name = _secret_name(key, prefix)
        try:
            value = client.get_secret(name).value
        except ResourceNotFoundError as e:
            raise RuntimeError(f"Missing required secret in Key Vault: {name}") from e
        except AzureError as e:
            # Sign-in and permission failures, e.g. a 403 from get_secret
            raise RuntimeError(f"Could not read secret {name!r} from Key Vault") from e
        if value is None:
            raise RuntimeError(f"Missing required secret in Key Vault: {name}")
        config[key] = value

    return config


def _load_aws_secrets(region: str | None, prefix: str) -> dict[str, str]:
    """Load secret config from AWS Secrets Manager."""
    try:
        import boto3
    except ImportError as e:
        raise RuntimeError(
            "AWS Secrets Manager needs boto3: pip install pymaskinporten[aws]"
        ) from e

    try:
        client = boto3.client("secretsmanager", region_name=region)
    except Exception as e:
        # e.g. NoRegionError when no region is given or configured
        raise RuntimeError("Could not create the AWS Secrets Manager client") from e

    config: dict[str, str] = {}

    for key in MaskinportenSecrets.model_fields:
        name = _secret_name(key, prefix)
        try:
            value = client.get_secret_value(SecretId=name).get("SecretString")
        except Exception as e:
            # botocore raises ClientError for missing secrets and access denied, and
            # its own errors for missing credentials
            raise RuntimeError(
                f"Could not read secret {name!r} from AWS Secrets Manager"
            ) from e
        if value is None:
            raise RuntimeError(
                f"Secret {name!r} in AWS Secrets Manager has no string value"
            )
        config[key] = value

    return config


def _load_gcp_secrets(project_id: str, prefix: str) -> dict[str, str]:
    """Load secret config from Google Secret Manager."""
    try:
        from google.cloud import secretmanager
    except ImportError as e:
        raise RuntimeError(
            "Google Secret Manager needs google-cloud-secret-manager: "
            "pip install pymaskinporten[gcp]"
        ) from e

    try:
        client = secretmanager.SecretManagerServiceClient()
    except Exception as e:
        # e.g. DefaultCredentialsError when no Application Default Credentials are set
        raise RuntimeError("Could not create the Google Secret Manager client") from e

    config: dict[str, str] = {}

    for key in MaskinportenSecrets.model_fields:
        name = _secret_name(key, prefix)
        path = f"projects/{project_id}/secrets/{name}/versions/latest"
        try:
            response = client.access_secret_version(name=path)
            config[key] = response.payload.data.decode("utf-8")
        except Exception as e:
            # google.api_core raises NotFound, PermissionDenied and similar
            raise RuntimeError(
                f"Could not read secret {name!r} from Google Secret Manager"
            ) from e

    return config
