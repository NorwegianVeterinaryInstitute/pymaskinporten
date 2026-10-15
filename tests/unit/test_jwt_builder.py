import jwt

from pymaskinporten.config import MaskinportenSecrets
from pymaskinporten.request_token import build_jwt

TEST_MASKINPORTEN_ISSUER = "https://test.maskinporten.no/"


def test_jwt_contains_expected_claims(real_private_key_pem):
    cfg = MaskinportenSecrets(
        PRIVATE_KEY=real_private_key_pem,
        MASKINPORTEN_CLIENT_ID="my-client",
        KID="my-kid",
        SCOPE="some:scope",
    )

    token = build_jwt(cfg, TEST_MASKINPORTEN_ISSUER)

    assert isinstance(token, str)

    decoded = jwt.decode(token, options={"verify_signature": False})

    assert decoded["iss"] == "my-client"
    assert decoded["aud"] == TEST_MASKINPORTEN_ISSUER
    assert decoded["scope"] == "some:scope"
    assert "iat" in decoded
    assert "exp" in decoded
    assert "jti" in decoded
