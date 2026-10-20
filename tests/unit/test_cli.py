from unittest.mock import patch

import httpx2 as httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

from pymaskinporten.cli import main
from pymaskinporten.config import MaskinportenSecrets
from pymaskinporten.request_token import MaskinportenTokenError


@pytest.fixture
def secrets(real_private_key_pem) -> MaskinportenSecrets:
    return MaskinportenSecrets(
        PRIVATE_KEY=real_private_key_pem,
        MASKINPORTEN_CLIENT_ID="client-id",
        KID="kid123",
        SCOPE="scope:a",
    )


@pytest.fixture
def loaded(secrets):
    with patch("pymaskinporten.cli.load_config", return_value=secrets) as load:
        yield load


@pytest.fixture
def mocked_request():
    with patch("pymaskinporten.cli.request_maskinporten_token") as request:
        request.return_value = ("secret-token", 120)
        yield request


@pytest.mark.unit
def test_success_prints_ok_without_secrets(secrets, loaded, mocked_request, capsys):
    assert main(["doctor"]) == 0

    out = capsys.readouterr().out
    assert "OK: got an access token, valid for 120 seconds." in out
    assert "https://test.maskinporten.no/token" in out
    assert "client-id" in out
    assert "secret-token" not in out
    assert secrets.PRIVATE_KEY not in out


@pytest.mark.unit
def test_options_are_passed_through(secrets, loaded, mocked_request):
    main(
        [
            "doctor",
            "--env",
            "prod",
            "--deployment",
            "aws",
            "--region",
            "eu-north-1",
            "--prefix",
            "mp/",
            "--token-url",
            "http://localhost:6969/token",
            "--audience",
            "http://localhost:6969/",
        ]
    )

    loaded.assert_called_once_with(
        "aws",
        secret_scope=None,
        key_vault_uri=None,
        region="eu-north-1",
        project_id=None,
        prefix="mp/",
    )
    mocked_request.assert_called_once_with(
        "prod",
        config=secrets,
        token_url="http://localhost:6969/token",
        audience="http://localhost:6969/",
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("error", "hint"),
    [
        (
            MaskinportenTokenError("Error 400", status=400, code="invalid_scope"),
            "scope is not granted",
        ),
        (
            MaskinportenTokenError("Error 401", status=401, code="invalid_client"),
            "client ID is unknown",
        ),
        (
            MaskinportenTokenError("Error 400", status=400, code="invalid_grant"),
            "rejected the JWT",
        ),
        (
            MaskinportenTokenError(
                "Error 400", status=400, code="x", description="AUTH-00004 failed"
            ),
            "catch-all",
        ),
        (
            MaskinportenTokenError("Error 500", status=500),
            "rejected the request",
        ),
        (MaskinportenTokenError("Request failed"), "No response from Maskinporten"),
        (
            MaskinportenTokenError("Unexpected token response", status=200),
            "Got a response, but no token",
        ),
    ],
)
def test_failure_prints_hint_and_checklist(loaded, mocked_request, capsys, error, hint):
    mocked_request.side_effect = error

    assert main(["doctor"]) == 1

    out = capsys.readouterr().out
    assert "FAILED" in out
    assert hint in out
    assert "Checklist:" in out


@pytest.mark.unit
def test_network_error_from_request_is_reported(secrets, loaded, capsys):
    with patch(
        "pymaskinporten.request_token.httpx.post",
        side_effect=httpx.ConnectError("refused"),
    ):
        assert main(["doctor"]) == 1

    assert "No response from Maskinporten" in capsys.readouterr().out


@pytest.mark.unit
def test_missing_credentials_are_reported(mocked_request, capsys):
    with patch(
        "pymaskinporten.cli.load_config",
        side_effect=RuntimeError("Missing required environment variable: KID"),
    ):
        assert main(["doctor"]) == 1

    assert "Could not load credentials: Missing required" in capsys.readouterr().out
    mocked_request.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize(
    "key",
    [
        "TOP-SECRET-KEY",
        # A PEM from an env var with literal \n instead of line breaks
        "-----BEGIN PRIVATE KEY-----\\nTOPSECRET\\n-----END PRIVATE KEY-----",
    ],
)
def test_unparsable_key_is_reported_without_value(
    monkeypatch, mocked_request, capsys, key
):
    # Strict validation is off by default, so load_config accepts any key
    monkeypatch.setenv("PRIVATE_KEY", key)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    assert main(["doctor"]) == 1

    out = capsys.readouterr().out
    assert "Invalid private key:" in out
    assert "literal \\n" in out
    assert "TOPSECRET" not in out and "TOP-SECRET-KEY" not in out
    mocked_request.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("key", "name"),
    [
        (ec.generate_private_key(ec.SECP256R1()), "ECPrivateKey"),
        (ed25519.Ed25519PrivateKey.generate(), "Ed25519PrivateKey"),
    ],
)
def test_non_rsa_key_is_reported(monkeypatch, mocked_request, capsys, key, name):
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    monkeypatch.setenv("PRIVATE_KEY", pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    assert main(["doctor"]) == 1

    out = capsys.readouterr().out
    assert f"got {name}" in out
    assert "must be an RSA private key" in out
    mocked_request.assert_not_called()


@pytest.mark.unit
def test_public_key_is_reported_as_invalid(
    monkeypatch, mocked_request, capsys, real_private_key_pem
):
    private = serialization.load_pem_private_key(
        real_private_key_pem.encode(), password=None
    )
    public_pem = (
        private.public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    monkeypatch.setenv("PRIVATE_KEY", public_pem)
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    assert main(["doctor"]) == 1

    assert "Invalid private key:" in capsys.readouterr().out
    mocked_request.assert_not_called()


@pytest.mark.unit
def test_invalid_credentials_do_not_print_values(monkeypatch, mocked_request, capsys):
    # With strict validation an unparsable key fails, and pydantic's own message
    # would include it
    monkeypatch.setenv("STRICT_KEY_VALIDATION", "1")
    monkeypatch.setenv("PRIVATE_KEY", "TOP-SECRET-KEY")
    monkeypatch.setenv("MASKINPORTEN_CLIENT_ID", "client-id")
    monkeypatch.setenv("KID", "kid123")
    monkeypatch.setenv("SCOPE", "scope:a")

    assert main(["doctor"]) == 1

    out = capsys.readouterr().out
    assert "Invalid credentials:" in out
    assert "PRIVATE_KEY" in out
    assert "TOP-SECRET-KEY" not in out
    mocked_request.assert_not_called()


@pytest.mark.unit
def test_command_is_required(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main([])

    assert excinfo.value.code == 2
