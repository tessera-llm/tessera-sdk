# Changelog

All notable changes to the Tessera SDK (Python + Node) are documented here. This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Pre-1.0 minor versions (`0.x.0`) may include breaking changes — pin a floor + ceiling in production (`tessera-llm-proxy>=0.1.0,<0.2`, `@tessera-llm/sdk@^0.1.0`).

## [Unreleased]

### Added

- PEP 561 `py.typed` marker on the Python package — autocomplete and `mypy --strict` now work without an external-package warning.
- `SECURITY.md` with a 90-day responsible-disclosure window and scope statement.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1).
- Issue templates (`bug_report`, `feature_request`) and a pull-request template under `.github/`.
- `dependabot.yml` to track npm, pip, and GitHub Actions update streams weekly.
- Push + pull-request CI workflow that runs typecheck, tests, and a published-artifact smoke test on Node 20/22 and Python 3.10/3.11/3.12.

### Changed

- README polish — clearer hero, worked example uses realistic gpt-4o list-price math, FAQ extended with rate-limits / PII / uptime / self-host coverage, comparison table no longer names third-party observability vendors directly.
- `LICENSE` replaced with the full Apache-2.0 text (was a 17-line summary) so GitHub correctly detects the license.
- `CONTRIBUTING.md` paths corrected (`python/` and `node/` — was `packages/tessera-llm SDK-python` etc.), single-license statement (Apache-2.0 only — was incorrectly listed as "dual-licensed"), and the Style section now points at the in-tree source conventions rather than an external workflow doc.

### Notes

- Behaviour and wire format are unchanged from `0.1.0` — no SDK-level breaking change in this batch.

## [0.1.0] — 2026-05-17

### Added

- Initial public release of the Tessera SDK (`tessera-llm-proxy` on PyPI, `@tessera-llm/sdk` on npm).
- One-line `tessera.activate()` (Python) / `activate()` (Node/TS) patches OpenAI, Anthropic, Mistral, Groq, and Cohere client constructors transparently in-process — point the underlying SDK at `api.tesseraai.io` and inject the Tessera key without rewriting your call sites.
- Manual wiring primitives `tessera.url(provider)` / `url(provider)` + `tessera.headers()` / `headers()` for providers without an official SDK (DeepSeek, xAI, Together, Fireworks, OpenRouter, Perplexity, Cerebras, Google Gemini AI Studio).
- `deactivate()` for test teardown; `status()` and `isActive()` / `is_active()` for health-check + logging integration.
- Apache-2.0 license, runnable examples in `examples/`.

### Documentation

- README with worked pricing example, optimisation reference, Quality SLA spec, supported-provider matrix, FAQ.
- Per-package READMEs in `python/` and `node/`.

[Unreleased]: https://github.com/tessera-llm/sdk/compare/python-v0.1.0...main
[0.1.0]: https://github.com/tessera-llm/sdk/releases/tag/python-v0.1.0
