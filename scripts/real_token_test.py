"""Request a real token from Maskinporten's test environment.

Reads the credentials from .env (see make_test_key.py); run from the repo root:

    uv run --extra web python scripts/real_token_test.py
"""

from dotenv import load_dotenv

import pymaskinporten as mp

load_dotenv()

token, expires_in = mp.request_maskinporten_token("test")
print(f"OK: got a token ({len(token)} chars), expires_in={expires_in}")
