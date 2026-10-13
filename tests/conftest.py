import textwrap

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture
def fake_pem() -> str:
    # Minimal-but-PEM-looking string
    return textwrap.dedent("""\
        -----BEGIN PRIVATE KEY-----
        MIIBVwIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEAuQ==
        -----END PRIVATE KEY-----
    """)


@pytest.fixture(autouse=True)
def clear_strict_validation_env(monkeypatch):
    """
    Ensure STRICT_KEY_VALIDATION is unset by default for each test,
    unless a test explicitly sets it.
    """
    monkeypatch.delenv("STRICT_KEY_VALIDATION", raising=False)


@pytest.fixture
def real_private_key_pem():
    """
    Generates a real RSA private key for test signing.
    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode("utf-8")
