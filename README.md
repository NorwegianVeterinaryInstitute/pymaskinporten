# pymaskinporten

<!-- badges start-->
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fnorwegianveterinaryinstitute%2Fpymaskinporten%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![PyPI version](https://img.shields.io/pypi/v/pymaskinporten.svg)](https://pypi.org/project/pymaskinporten/)
[![CI](https://github.com/norwegianveterinaryinstitute/pymaskinporten/actions/workflows/ci.yml/badge.svg?branch=main)](.github/workflows/ci.yml)
[![release-please](https://github.com/norwegianveterinaryinstitute/pymaskinporten/actions/workflows/release-please.yml/badge.svg)](release-please-config.json)
[![Docs (pdoc to GitHub Pages)](https://github.com/norwegianveterinaryinstitute/pymaskinporten/actions/workflows/docs.yml/badge.svg)](https://github.com/norwegianveterinaryinstitute/pymaskinporten/actions/workflows/docs.yml)
[![PyPI](https://github.com/norwegianveterinaryinstitute/pymaskinporten/actions/workflows/publish.yml/badge.svg)](https://github.com/norwegianveterinaryinstitute/pymaskinporten/actions/workflows/publish.yml)
[![Dependabot](https://img.shields.io/github/issues-search?query=repo%3Anorwegianveterinaryinstitute%2Fpymaskinporten%20is%3Apr%20author%3Aapp%2Fdependabot%20is%3Aopen&label=Dependabot%20PRs)](https://github.com/norwegianveterinaryinstitute/pymaskinporten/issues?q=is%3Apr%20is%3Aopen%20author%3Aapp%2Fdependabot)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![License](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://opensource.org/license/apache-2.0)
<!-- badges end-->

This is a python package to request a token from [Maskinporten](https://samarbeid.digdir.no/maskinporten/dette-er-maskinporten/96) - the Norwegian 
national access control solution for businesses that exchange data.

```mermaid
graph LR
  Consumer["Application"] -- request token ---> Maskinporten
  Maskinporten -- issue new token ---> Consumer
  Consumer -- use token ---> Service["External Service"]
```

## Example usage

This assumes that: 
1. You have created the integration on digidir.no and,
2. You have set the necessary environment variables for your API credentials.

```python
# set environment variables for your API    
import os
os.environ["KID"] = "your_kid"
os.environ["PRIVATE_KEY"] = "your_private_key"
os.environ["MASKINPORTEN_CLIENT_ID"] = "your_client_id"
os.environ["SCOPE"] = "your_scope"

# get the access token
from pymaskinporten.request_token import request_maskinporten_token
access_token, expires_in = request_maskinporten_token("my_api", "test")
print(f"Access Token: {access_token}")
print(f"Expires In: {expires_in} seconds")
```

## Docker container 

If you want to test the library through a web browser the image opens a `flask` app:

```bash
cat > .env <<EOF
>PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
>MASKINPORTEN_CLIENT_ID="your-client-id"
>KID="your-kid"
>SCOPE="your-scope"
>STRICT_KEY_VALIDATION=false
>EOF

docker run -p 5000:5000 --env-file .env ghcr.io/norwegianveterinaryinstitute/pymaskinporten:main
```
