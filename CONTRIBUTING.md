# Contributing to tessera-llm SDK

Thanks for your interest. SDKs are dual-licensed and PRs welcome.

## Reporting bugs

Open an issue at
[github.com/tessera-llm/sdk/issues](https://github.com/tessera-llm/sdk/issues)
with:

- SDK version (`tessera-llm SDK` from `pip list` or `npm list`)
- Language version
- Minimum repro snippet
- Expected vs actual behavior

If the bug touches measurement / billing, include your client_id (visible in
`/portal/settings`) so we can trace the request_id.

## Development setup

### Python

```bash
cd packages/tessera-llm SDK-python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Node / TypeScript

```bash
cd packages/tessera-llm SDK-node
npm install
npm test
npm run build
```

## What we want

- New adapter examples in `packages/examples/` for frameworks not yet
  covered (Vercel AI SDK, Mastra, LlamaIndex.TS, Haystack, DSPy)
- Bug fixes with reproducing test
- Documentation improvements
- Type stub improvements for TypeScript

## What we don't want (yet)

- Multi-SDK rewrites or reimplementation of upstream provider clients
- Breaking changes to the `activate()` / `url()` / `headers()` public API
- Telemetry / analytics added to the SDK (we already capture measurement
  via the proxy; SDK should stay slim)
- Vendored dependencies — keep the SDK installable from a single
  PyPI / npm tag

## Style

- **Python**: Black-formatted, type hints on public surfaces, pytest tests
  alongside the code they exercise
- **TypeScript**: Prettier-formatted (`.prettierrc`), explicit return
  types on public exports, vitest tests
- **Both**: docstrings on every public function explaining WHY not just
  WHAT. Mirror the project-level convention (see CLAUDE.md if working
  in the monorepo).

## License

By contributing, you agree your contribution is licensed under Apache-2.0
matching the rest of the SDK.

## Contact

- Bug reports: GitHub Issues
- Security: [security@tesseraai.io](mailto:security@tesseraai.io)
- General: [founder@tesseraai.io](mailto:founder@tesseraai.io)
