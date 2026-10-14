# smoke_test.py
# Run against the built wheel/sdist in publish.yml: the public API imports and can sign a JWT.
# Any exception exits non-zero and fails the workflow.

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from pymaskinporten import MaskinportenSecrets, build_jwt

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pem = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode()
cfg = MaskinportenSecrets(
    PRIVATE_KEY=pem, MASKINPORTEN_CLIENT_ID="client", KID="kid", SCOPE="scope"
)
assert build_jwt(cfg, "https://test.maskinporten.no/token")
print("Smoke test passed: public API imported and signed a JWT")
