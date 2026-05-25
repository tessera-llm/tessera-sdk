# Changelog

All notable changes to the Tessera SDK (Python + Node) are documented here. This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Pre-1.0 minor versions (`0.x.0`) may include breaking changes — pin a floor + ceiling in production (`tessera-llm-proxy>=0.1.0,<0.2`, `@tessera-llm/tessera-sdk@^0.1.0`).

## [Unreleased]

## [0.1.3] -- 2026-05-25

### Fixed
- Broken `Get free API key` CTA in README + node/python sub-READMEs + examples that linked to `ledger.tesseraai.io/signup-dev` (returns 404 on dashboard subdomain). Canonical signup URL is `tesseraai.io/dev`. Founder caught customer-facing bug 2026-05-25 EOD.

## [0.1.2] -- 2026-05-25

### Fixed
- tk_ prefix sweep across docs + test fixtures (post-0.1.1 follow-up).
- Free Dev -> Free Sandbox terminology consistency across READMEs.

### Changed
- Companion-cross-link block refreshed to include 4 new sibling repos
  (tessera-mastra, tessera-pydantic-ai, tessera-crewai, tessera-autogen).
_Nothing yet._

## [0.1.1] — 2026-05-19

### Added

- PEP 561 `py.typed` marker on the Python package — autocomplete and `mypy --strict` now recognise the package as typed (no more "Skipping analyzing 'tessera'" warning).
- `SECURITY.md` with a 90-day responsible-disclosure window and an explicit scope statement.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1) with enforcement contact at `conduct@tesseraai.io`.
- Issue templates (`bug_report.yml`, `feature_request.yml`) and a pull-request template under `.github/`.
- `dependabot.yml` tracking npm, pip, and GitHub Actions update streams weekly.
- Push + pull-request CI workflow at `.github/workflows/ci.yml` running typecheck + tests across Node 18 / 20 / 22 and Python 3.9 / 3.10 / 3.11 / 3.12.
- `node/package-lock.json` checked in so CI's `setup-node` cache step resolves deterministically.

### Changed

- README polish — clearer hero ("LLM gateway" in the opening, "substrate proxy" reserved for the comparison section), worked-example math anchored on realistic gpt-4o list rates at 5B tokens / month, "you keep 80%" framing on pricing, four new pre-buy FAQ entries (rate limits, PII, proxy uptime, self-host), comparison table no longer names individual observability vendors, and a new Type safety section.
- Free Sandbox rate limit raised from 10 → 30 req/min on both the worker and the documented copy. Generous enough that hobby + side-projects almost never hit it; still clearly below Production's 60 rpm.
- M-code mechanic identifiers downgraded to `<sub>(m1)</sub>` sub-identifiers in the mechanic table and stripped from the SLA narrative prose. The `/portal/audit` chip strip still uses the same lowercase codes for power users matching audit logs.
- Worker now exposes `GET /health` returning `{status, worker, environment, ts}` JSON alongside the existing `/healthz` plain-text liveness probe. Pingdom, Better Uptime, Cloudflare Health Checks all expect the `/health` convention.
- `LICENSE` replaced with the full Apache-2.0 text (was a 17-line summary) so GitHub correctly detects the license as `apache-2.0` instead of "Other".
- `CONTRIBUTING.md` paths corrected (`python/` and `node/`, was `packages/tessera-llm SDK-*`), single-license statement (Apache-2.0 only, was incorrectly listed as "dual-licensed"), and the Style section now points at the in-tree source conventions.
- `python/pyproject.toml` adds a `[dev]` extras alias mirroring `[test]` so `pip install -e ".[dev]"` (as `CONTRIBUTING.md` documents) works; the wheel target now includes the `py.typed` marker; the Changelog URL points at this file directly.

### Notes

- Behaviour and wire format are unchanged from `0.1.0`. Pin floor + ceiling per the install table at the top of the README.

## [0.1.0] — 2026-05-17

### Added

- Initial public release of the Tessera SDK (`tessera-llm-proxy` on PyPI, `@tessera-llm/tessera-sdk` on npm).
- One-line `tessera.activate()` (Python) / `activate()` (Node/TS) patches OpenAI, Anthropic, Mistral, Groq, and Cohere client constructors transparently in-process — point the underlying SDK at `api.tesseraai.io` and inject the Tessera key without rewriting your call sites.
- Manual wiring primitives `tessera.url(provider)` / `url(provider)` + `tessera.headers()` / `headers()` for providers without an official SDK (DeepSeek, xAI, Together, Fireworks, OpenRouter, Perplexity, Cerebras, Google Gemini AI Studio).
- `deactivate()` for test teardown; `status()` and `isActive()` / `is_active()` for health-check + logging integration.
- Apache-2.0 license, runnable examples in `examples/`.

### Documentation

- README with worked pricing example, optimisation reference, Quality SLA spec, supported-provider matrix, FAQ.
- Per-package READMEs in `python/` and `node/`.

[Unreleased]: https://github.com/tessera-llm/tessera-sdk/compare/python-v0.1.1...main
[0.1.1]: https://github.com/tessera-llm/tessera-sdk/compare/python-v0.1.0...python-v0.1.1
[0.1.0]: https://github.com/tessera-llm/tessera-sdk/releases/tag/python-v0.1.0
