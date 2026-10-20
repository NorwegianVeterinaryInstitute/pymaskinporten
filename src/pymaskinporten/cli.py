"""The pymaskinporten command line: `pymaskinporten doctor` checks a Maskinporten setup."""

import argparse
import sys

from pydantic import ValidationError

from pymaskinporten.config import load_config
from pymaskinporten.request_token import (
    MaskinportenTokenError,
    _resolve_endpoints,
    request_maskinporten_token,
)

CHECKLIST = [
    "Right environment? test and prod are separate integrations in Samarbeidsportalen.",
    "Is the scope granted to this integration by the API owner?",
    "Is the public key registered on the integration, and does KID match its key ID?",
    "Is MASKINPORTEN_CLIENT_ID the integration ID of the same environment?",
    "Is the clock on this machine correct?",
]


def _hint(error: MaskinportenTokenError) -> str:
    """The likely cause of a failed token request, from Maskinporten's error code."""
    code = (error.code or "").lower()
    text = f"{error.code or ''} {error.description or ''}".lower()

    if error.status is None:
        return (
            "No response from Maskinporten: check the token URL, network access and "
            "any proxy."
        )
    if "auth-00004" in text:
        return "AUTH-00004 is a catch-all error: work through the checklist below."
    if code == "invalid_client":
        return (
            "The client ID is unknown in this environment, or the key (KID) is not "
            "registered on the integration."
        )
    if code == "invalid_scope":
        return (
            "The scope is not granted to this integration, or it is misspelled. Ask "
            "the API owner to grant it."
        )
    if code == "invalid_grant":
        return (
            "Maskinporten rejected the JWT. Common causes: the key does not match KID, "
            "the audience is not the environment's issuer, or the clock is off."
        )
    return "Maskinporten rejected the request: see the checklist below."


def _doctor(args: argparse.Namespace) -> int:
    try:
        token_url, audience = _resolve_endpoints(
            args.env, args.token_url, args.audience
        )
        config = load_config(
            args.deployment,
            secret_scope=args.secret_scope,
            key_vault_uri=args.key_vault_uri,
            region=args.region,
            project_id=args.project_id,
            prefix=args.prefix,
        )
    except ValidationError as e:
        # Report only which fields failed: str(e) would include their values,
        # among them the private key
        print("Invalid credentials:")
        for err in e.errors():
            field = ".".join(str(part) for part in err["loc"])
            print(f"  {field}: {err['msg']}")
        return 1
    except (ValueError, RuntimeError) as e:
        print(f"Could not load credentials: {e}")
        return 1

    print(f"Environment: {args.env}")
    print(f"Token URL:   {token_url}")
    print(f"Audience:    {audience}")
    print(f"Client ID:   {config.MASKINPORTEN_CLIENT_ID}")
    print(f"KID:         {config.KID}")
    print(f"Scope:       {config.SCOPE}")
    print()

    try:
        _, expires_in = request_maskinporten_token(
            args.env, config=config, token_url=token_url, audience=audience
        )
    except MaskinportenTokenError as e:
        print(f"FAILED: {e}")
        if e.code:
            print(f"Error code:  {e.code}")
        if e.description:
            print(f"Description: {e.description}")
        print()
        print(f"Likely cause: {_hint(e)}")
        print()
        print("Checklist:")
        for item in CHECKLIST:
            print(f"  - {item}")
        return 1

    print(f"OK: got an access token, valid for {expires_in} seconds.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pymaskinporten", description="Tools for Maskinporten integrations."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser(
        "doctor",
        help="request a token and explain why it fails",
        description="Request a Maskinporten token with your credentials and explain "
        "a failure. Never prints the private key or the token.",
    )
    doctor.add_argument("--env", choices=["test", "prod"], default="test")
    doctor.add_argument(
        "--deployment",
        choices=["local", "azure", "databricks", "aws", "gcp"],
        default="local",
        help="where to read the credentials from (default: environment variables)",
    )
    doctor.add_argument("--prefix", default="", help="prefix of the secret names")
    doctor.add_argument("--secret-scope", help="Databricks secret scope")
    doctor.add_argument("--key-vault-uri", help="Azure Key Vault URL")
    doctor.add_argument("--region", help="AWS region")
    doctor.add_argument("--project-id", help="Google Cloud project ID")
    doctor.add_argument("--token-url", help="token endpoint to call instead")
    doctor.add_argument("--audience", help="JWT audience to use instead")
    doctor.set_defaults(func=_doctor)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
