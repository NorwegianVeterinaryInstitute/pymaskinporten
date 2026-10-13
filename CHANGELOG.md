# Changelog

## [1.1.3](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.2...v1.1.3) (2026-10-13)


### Bug Fixes

* **deps:** require patched pyjwt and httpx2, drop unused jwcrypto ([#109](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/109)) ([a0ed5d6](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/a0ed5d66cdf81f2eed3a15795d3140d83b807d38)), closes [#108](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/issues/108)

## [1.1.2](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/v1.1.1...v1.1.2) (2026-07-03)


### Documentation

* update docs to use great-docs. ([da3ebb0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/da3ebb0629556543a23adba02b79fbdadf0c73d9))
* update docs to use great-docs. ([fdbbf50](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/fdbbf50c2c6823a12f43338cfee4f538015104e6))

## [1.1.1](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/pymaskinporten-v1.1.0...pymaskinporten-v1.1.1) (2026-03-12)


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

## [1.1.0](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/compare/pymaskinporten-v1.0.0...pymaskinporten-v1.1.0) (2026-03-12)


### Features

* add azure key valut logic for config ([b128692](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/b12869278e0010ff5ff26c61d85d0808a72ef0df))
* add azure key valut logic for config ([c8c25de](https://github.com/NorwegianVeterinaryInstitute/pymaskinporten/commit/c8c25ded73ff34f6da96b9218d86122820e5b0d5))

## [1.0.0](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/pymaskinporten-v0.11.0...pymaskinporten-v1.0.0) (2026-03-09)


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

## [0.11.0](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/py_maskinporten-v0.10.5...py_maskinporten-v0.11.0) (2026-03-09)


### Features

* add logic to handle secrets from azure key vault in databricks ([b7a5067](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/b7a50672e98da498813ffdabb6e4585b5ecf24b9))
* add pydantic model for config ([5c9db87](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/5c9db875f24b0317e390816bbdb8a963d10d9643))


### Bug Fixes

* don't set the env vars in dockerfile ([b569cc1](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/b569cc10fb7b6fe666b1f84a296b6a66346a9127))

## [0.10.5](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/py_maskinporten-v0.10.4...py_maskinporten-v0.10.5) (2026-03-06)


### Bug Fixes

* update dependencies in toml ([c1ab5ff](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/c1ab5ff201b50576a6c0adee1c22eb1200ad496d))

## [0.10.4](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/compare/py_maskinporten-v0.10.3...py_maskinporten-v0.10.4) (2026-03-06)


### Documentation

* update README.md ([40ee683](https://github.com/NorwegianVeterinaryInstitute/py_maskinporten/commit/40ee683475508387f5e1d99da6fc86a1f6bef2f8))

## [0.10.3](https://github.com/novica/py_maskinporten/compare/py_maskinporten-v0.10.2...py_maskinporten-v0.10.3) (2026-03-06)


### Documentation

* Update README.md ([a1f8eda](https://github.com/novica/py_maskinporten/commit/a1f8edac704b4dc479d80c1e82712bf6abcf9421))

## [0.10.2](https://github.com/novica/py_maskinporten/compare/py_maskinporten-v0.10.1...py_maskinporten-v0.10.2) (2026-03-06)


### Bug Fixes

* docker image runs the app ([be6ac59](https://github.com/novica/py_maskinporten/commit/be6ac5970496aa98e47aa03257e0d0edb0474af6))

## [0.10.1](https://github.com/novica/py_maskinporten/compare/py_maskinporten-v0.10.0...py_maskinporten-v0.10.1) (2026-03-06)


### Documentation

* Add mermaid diagram for token request flow ([52516b6](https://github.com/novica/py_maskinporten/commit/52516b65886ba7689f8c8cc0dcbba305015ed9a5))

## [0.10.0](https://github.com/novica/py_maskinporten/compare/py_maskinporten-v0.9.0...py_maskinporten-v0.10.0) (2026-03-06)


### Features

* flask app for token fetching ([4713527](https://github.com/novica/py_maskinporten/commit/4713527bb414088a5f52bfc62490f3f4fe7d09bd))


### Documentation

* update readme ([5e56cc4](https://github.com/novica/py_maskinporten/commit/5e56cc40d6dd7d753c7247cb27979bdacf3fbdbc))
