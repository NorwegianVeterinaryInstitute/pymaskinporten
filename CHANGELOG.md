# Changelog

## [2.1.0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v2.0.1...v2.1.0) (2026-10-20)


### Features

* add MaskinportenClient with token caching ([#149](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/149)) ([4f860af](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/4f860afd4926e553ce162e4acb5a76e26b51ae30))
* add pymaskinporten doctor command ([#150](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/150)) ([61569a6](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/61569a630ab4a0f88d9c6a37a43daa787ada647e))
* add status, code and description to errors ([#141](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/141)) ([3348950](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/3348950e8674c49c0c4f9124424bbd888d65d123))
* allow overriding token endpoint and audience ([#148](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/148)) ([4626979](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/46269798621ccf40a4bef4a32b7bbe4ec4b7ea46))


### Bug Fixes

* report bad private keys in doctor ([#151](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/151)) ([0237629](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/0237629c571980caf39a069938ef405b6ed556f9))


### Documentation

* improve package discoverability ([#135](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/135)) ([b4b0441](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/b4b0441fd1e67293faca5447e12ab12aeca5c57a))

## [2.0.1](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v2.0.0...v2.0.1) (2026-10-15)


### Bug Fixes

* use the Maskinporten issuer as the JWT audience ([#130](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/130)) ([7b40129](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/7b401293a493fee4c953268f14f9186fb79e6951))

## [2.0.0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.4...v2.0.0) (2026-10-15)


### ⚠ BREAKING CHANGES

* the maskinporten-web command is now pymaskinporten-web.
* maskinporten-web needs pip install pymaskinporten[web]. Install pymaskinporten[web,azure] for the dependencies 1.x installed by default.
* the Azure Key Vault loader needs pip install pymaskinporten[azure].
* the placeholder pymaskinporten.main() and the pymaskinporten console script are removed.
* load_config() no longer calls load_dotenv(). Call it yourself before load_config() if you rely on a .env file.
* request_maskinporten_token raises ValueError unless api_env is "test" or "prod".

### Features

* add a databricks extra for the Databricks secret loader ([60ced8c](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/60ced8c1070eb1539c06962278336cd99176c853)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)
* add a prefix for credential names in every source ([37d05a2](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/37d05a24fdcd5d9a9a78d51333ed9a79f5ac58f9)), closes [#122](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/122)
* export the public API from the package root ([f4465c8](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/f4465c87cd03af0551b1dcde17a8b8f5e2a810bc)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)
* load credentials from AWS Secrets Manager ([b581974](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/b581974f1f7bfa017770028c7d9af0979439be7c)), closes [#122](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/122)
* load credentials from Google Secret Manager ([b425eda](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/b425eda8d6b9a4d12ed0af88023bd8840ff6b347)), closes [#122](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/122)
* move Flask and python-dotenv to an optional web extra ([8849cc3](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/8849cc3badd52c151c2d003334c8d3d988f8b454)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)
* move the Azure SDK to an optional azure extra ([3ed9396](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/3ed9396dd7d5b907e2aaa6618fde8d5df11cc7d5)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)
* rename the demo command to pymaskinporten-web ([26a5c37](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/26a5c3707e67fc7634a29403475320daeb20a04c)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)
* stop loading .env files inside load_config ([61c0039](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/61c003998e75ea6c187edfb2616752b06a9bf269)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)
* validate api_env and accept credentials through config= ([8500e12](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/8500e12488f9ef6b64cbc92cb33665e279d4ff2f)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)


### Bug Fixes

* make the Databricks secret loader work and use dashed secret names ([fc62c1e](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/fc62c1ee16fc506f4a890e9f6ab45a25b950544b)), closes [#115](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/115)
* raise MaskinportenTokenError for network errors and bad token responses ([74ba584](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/74ba5843f78baae627d68321fc755b194c2ade66)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)
* reject blank credential fields and strip surrounding whitespace ([8a9d76f](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/8a9d76f943936ceb6b5b25c378c962af08165c80)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)
* show invalid demo config on the page instead of a 500 ([74df35c](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/74df35ce59a572207af5c73f4cc3648324c39c01)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)
* use valid Key Vault secret names and report missing secrets ([5e7bcbb](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/5e7bcbb09f64f245d9e6eada37af835a9bbcc8f9)), closes [#115](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/115)
* wrap Databricks setup errors outside Databricks in RuntimeError ([ab3770b](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/ab3770b624b6fcba8a8ae901d457fbb2011f6500)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)
* wrap Key Vault access failures in RuntimeError ([1516183](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/15161831f07974f0cefa6572ffd9581b88acc48c)), closes [#115](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/115)


### Documentation

* document config=, root imports and .env loading ([2765dd0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/2765dd0fef37f22549e671e68ad02e7b50b65722)), closes [#114](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/114)
* document installing the extras ([eb9bd70](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/eb9bd7023c37f5e928ba860a42f9ba0ab96058b9)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)
* document the AWS and Google loaders and name prefixes ([4a47532](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/4a475326f323d8177e9afa1b157fd18810a3a766)), closes [#122](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/122)
* document the Key Vault and Databricks secret loaders ([34f3cd7](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/34f3cd706144dac675ecd446c8aab970e6d04064)), closes [#115](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/115)
* put prefix example comments on their own lines ([5805cb9](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/5805cb94fecd620439d70a5de2fae8335fb6cbe8))
* say the secret-store loaders are untested against real services ([ab60b5f](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/ab60b5f5b4003c7bd7ab8a5081ec74ec3964c7c2)), closes [#116](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/116)

## [1.1.4](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.3...v1.1.4) (2026-10-14)


### Bug Fixes

* Docker entrypoint, README example, and local-only demo bind ([#119](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/119)) ([8c6e9b6](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/8c6e9b645eb5a066d1bd69c16f27d118bcab474f)), closes [#113](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/113)

## [1.1.3](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.2...v1.1.3) (2026-10-13)


### Bug Fixes

* **deps:** require patched pyjwt and httpx2, drop unused jwcrypto ([#109](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/109)) ([a0ed5d6](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/a0ed5d66cdf81f2eed3a15795d3140d83b807d38)), closes [#108](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/108)

## [1.1.2](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.1...v1.1.2) (2026-07-03)


### Documentation

* update docs to use great-docs. ([da3ebb0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/da3ebb0629556543a23adba02b79fbdadf0c73d9))
* update docs to use great-docs. ([fdbbf50](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/fdbbf50c2c6823a12f43338cfee4f538015104e6))

## [1.1.1](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.0...v1.1.1) (2026-03-12)


### Bug Fixes

* actions to be able to write ([ca5238d](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/ca5238ddc5f5508afe425319127a86ac1f68c87b))
* actions to be able to write ([7aef9d4](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/7aef9d48c4b64eb9c39a9658b6f00c8b6af21783))
* **docs:** deploy to gh pages ([4a3b900](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/4a3b900b3dcff2e89b0e99e39a4d132f0252c64d))
* **docs:** deploy to gh pages ([0c647a1](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/0c647a18b844fbfec8307b7961cb17d3d1153769))
* **docs:** missing dependencies in workflow ([11d8672](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/11d86729de8a571e18f47485e9c90b904ade1480))
* **docs:** missing dependencies in workflow ([7a112c3](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/7a112c3afe94c85f6396cdeac4e2f8b36653d739))
* gh-pages deployment ([932227b](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/932227bd20580e9bd3d484b88db5ab4313d87eca))
* gh-pages deployment ([fc78182](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/fc781825a59d20cdb3f1e4cb15a810fd50137162))


### Documentation

* add GitHub Actions workflow for building and deploying document… ([f0bf9c8](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/f0bf9c827d20d44ee578f1b8803bc9991dc0f64d))
* add GitHub Actions workflow for building and deploying documentation to GitHub Pages ([94e4863](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/94e48634c61963da2aa7409ab2dc2d412778ef64))

## [1.1.0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.0.0...v1.1.0) (2026-03-12)


### Features

* add azure key valut logic for config ([b128692](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/b12869278e0010ff5ff26c61d85d0808a72ef0df))
* add azure key valut logic for config ([c8c25de](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/c8c25ded73ff34f6da96b9218d86122820e5b0d5))

## [1.0.0](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/v0.11.0...v1.0.0) (2026-03-09)


### ⚠ BREAKING CHANGES

* to avoid confusion between - and _ in imports and package name, we rename the project to 'pymaskinporten'

### Features

* add logic to handle secrets from azure key vault in databricks ([b7a5067](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/b7a50672e98da498813ffdabb6e4585b5ecf24b9))
* add pydantic model for config ([5c9db87](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/5c9db875f24b0317e390816bbdb8a963d10d9643))
* flask app for token fetching ([4713527](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/4713527bb414088a5f52bfc62490f3f4fe7d09bd))
* rename project to not include dashes or underscores in the name ([ff11be6](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/ff11be6263a1321940fecc9225290748e7ad62f2))


### Bug Fixes

* docker image runs the app ([be6ac59](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/be6ac5970496aa98e47aa03257e0d0edb0474af6))
* don't set the env vars in dockerfile ([b569cc1](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/b569cc10fb7b6fe666b1f84a296b6a66346a9127))
* update dependencies in toml ([c1ab5ff](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/c1ab5ff201b50576a6c0adee1c22eb1200ad496d))


### Documentation

* Add mermaid diagram for token request flow ([52516b6](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/52516b65886ba7689f8c8cc0dcbba305015ed9a5))
* update readme ([5e56cc4](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/5e56cc40d6dd7d753c7247cb27979bdacf3fbdbc))
* update README.md ([40ee683](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/40ee683475508387f5e1d99da6fc86a1f6bef2f8))
* Update README.md ([a1f8eda](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/a1f8edac704b4dc479d80c1e82712bf6abcf9421))

## [0.11.0](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/v0.10.5...v0.11.0) (2026-03-09)


### Features

* add logic to handle secrets from azure key vault in databricks ([b7a5067](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/b7a50672e98da498813ffdabb6e4585b5ecf24b9))
* add pydantic model for config ([5c9db87](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/5c9db875f24b0317e390816bbdb8a963d10d9643))


### Bug Fixes

* don't set the env vars in dockerfile ([b569cc1](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/b569cc10fb7b6fe666b1f84a296b6a66346a9127))

## [0.10.5](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/v0.10.4...v0.10.5) (2026-03-06)


### Bug Fixes

* update dependencies in toml ([c1ab5ff](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/c1ab5ff201b50576a6c0adee1c22eb1200ad496d))

## [0.10.4](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/v0.10.3...v0.10.4) (2026-03-06)


### Documentation

* update README.md ([40ee683](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/40ee683475508387f5e1d99da6fc86a1f6bef2f8))

## [0.10.3](https://github.com/novica/py_maskinporten/compare/v0.10.2...v0.10.3) (2026-03-06)


### Documentation

* Update README.md ([a1f8eda](https://github.com/novica/py_maskinporten/commit/a1f8edac704b4dc479d80c1e82712bf6abcf9421))

## [0.10.2](https://github.com/novica/py_maskinporten/compare/v0.10.1...v0.10.2) (2026-03-06)


### Bug Fixes

* docker image runs the app ([be6ac59](https://github.com/novica/py_maskinporten/commit/be6ac5970496aa98e47aa03257e0d0edb0474af6))

## [0.10.1](https://github.com/novica/py_maskinporten/compare/v0.10.0...v0.10.1) (2026-03-06)


### Documentation

* Add mermaid diagram for token request flow ([52516b6](https://github.com/novica/py_maskinporten/commit/52516b65886ba7689f8c8cc0dcbba305015ed9a5))

## [0.10.0](https://github.com/novica/py_maskinporten/compare/v0.9.0...v0.10.0) (2026-03-06)


### Features

* flask app for token fetching ([4713527](https://github.com/novica/py_maskinporten/commit/4713527bb414088a5f52bfc62490f3f4fe7d09bd))


### Documentation

* update readme ([5e56cc4](https://github.com/novica/py_maskinporten/commit/5e56cc40d6dd7d753c7247cb27979bdacf3fbdbc))
