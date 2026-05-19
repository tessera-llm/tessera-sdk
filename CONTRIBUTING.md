# Contributing to the Tessera SDK

Thanks for your interest. The Tessera SDK is Apache-2.0 licensed and PRs are welcome.

## Reporting bugs

Open an issue at
[github.com/tessera-llm/tessera-sdk/issues](https://github.com/tessera-llm/tessera-sdk/issues)
with:

- SDK version (`pip show tessera-llm-proxy` or `npm list @tessera-llm/tessera-sdk`)
- Language runtime version (Python 3.x, Node version)
- Minimum reproduction snippet
- Expected vs. actual behaviour

If the bug touches measurement or billing, include your `client_id` (visible at `/portal/billing` in the dashboard) so we can trace the corresponding `request_id` in proxy logs.

For security vulnerabilities, see [`SECURITY.md`](./SECURITY.md) — please do not file public issues.

## Development setup

### Python

```bash
cd python
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

### Node / TypeScript

```bash
cd node
npm install
npm test
npm run build
```

The CI workflow at `.github/workflows/ci.yml` runs the same checks on every push and pull request — keep it green.

## What we want

- New adapter examples in `examples/` for frameworks not yet covered (Vercel AI SDK, Mastra, LlamaIndex.TS, Haystack, DSPy).
- Bug fixes shipped with a reproducing test.
- Documentation improvements.
- Type stub improvements on the TypeScript side; expansion of typed surfaces on the Python side.

## What we don't want (yet)

- Multi-SDK rewrites or reimplementation of upstream provider clients.
- Breaking changes to the `activate()` / `url()` / `headers()` public API.
- Telemetry or analytics added to the SDK itself — measurement happens at the proxy. The SDK stays slim.
- Vendored dependencies — keep both packages installable from a single PyPI / npm tag.

## Style

- **Python:** Black-formatted, type hints on every public function, pytest tests sitting alongside the code they exercise.
- **TypeScript:** Prettier-formatted (see `node/.prettierrc`), explicit return types on every public export, vitest tests.
- **Both:** docstrings explain *why* a function exists, not just *what* it does. Mirror the conventions already established in `python/tessera/` and `node/src/` — small files, single responsibility, no premature abstraction.

By contributing, you agree your contribution is licensed under Apache-2.0 matching the rest of the SDK.

## Contact

- Bug reports: GitHub Issues.
- Security: [security@tesseraai.io](mailto:security@tesseraai.io).
- Code of Conduct enforcement: [conduct@tesseraai.io](mailto:conduct@tesseraai.io) — see [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).
- General: [founder@tesseraai.io](mailto:founder@tesseraai.io).
