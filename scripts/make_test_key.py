"""Generate an RSA key pair for a Maskinporten test integration.

Writes a new .env with the private key (PRIVATE_KEY), the public key to paste
into Samarbeidsportalen (PUBLIC_KEY) and placeholders for the rest. Run from the
repo root; never commit .env.

    uv run --extra web python scripts/make_test_key.py
"""

import pathlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

env = pathlib.Path(".env")
if env.exists():
    raise SystemExit(".env already exists; move it away first")

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

private_pem = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode()
public_pem = (
    key.public_key()
    .public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    .decode()
)

env.write_text(
    f'PRIVATE_KEY="{private_pem}"\n'
    "# Paste into the integration's keys in Samarbeidsportalen; not read by pymaskinporten\n"
    f'PUBLIC_KEY="{public_pem}"\n'
    "KID=<kid the portal shows for the key>\n"
    "MASKINPORTEN_CLIENT_ID=<integration id>\n"
    "SCOPE=<scope granted to the integration>\n"
)
print("Wrote .env. Paste PUBLIC_KEY into the integration, then fill in the rest.")
