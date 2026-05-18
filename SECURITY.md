# Security Policy

If you find a vulnerability in the Tessera SDK or in the way it interacts with the Tessera proxy, please report it privately.

**Email:** security@tesseraai.io

We aim to acknowledge reports within two business days and to ship a fix or a public mitigation note within 90 days of the initial report. If a report is materially time-sensitive (active exploitation, credential exposure) we cut a release immediately and notify all PyPI / npm installs on next install.

## Scope

In scope:

- The published Python package `tessera-llm-proxy` on PyPI.
- The published npm package `@tessera-llm/sdk`.
- The runnable examples in `examples/`.
- The wire format the SDK uses to talk to the Tessera proxy at `api.tesseraai.io` (header names, redirect rules, auth surface).

Out of scope:

- The internal implementation of the Tessera proxy itself (we treat the proxy as a hosted service — please report proxy-side vulnerabilities the same way; we do not publish the proxy source).
- The Tessera dashboard at `ledger.tesseraai.io` — report dashboard vulnerabilities to the same email; we treat them with the same SLA.
- Provider SDKs we patch (OpenAI, Anthropic, Mistral, Groq, Cohere) — report to the upstream maintainer first; we will fast-follow.

## What to include

A clean reproduction is the fastest path to a fix. Please include:

1. SDK language and version (`pip show tessera-llm-proxy` / `npm list @tessera-llm/sdk`).
2. Minimal repro code or a curl command.
3. Expected behaviour vs. observed behaviour.
4. Any logs, stack traces, or HTTP responses.

If your report includes potentially sensitive data (a prompt, an API key fragment, customer identifiers), encrypt the payload with our PGP key on request — email `security@tesseraai.io` and we will send the key.

## Disclosure

We follow a 90-day responsible disclosure window. If we acknowledge a report and ship a fix, we credit reporters in the corresponding `CHANGELOG.md` entry unless the reporter prefers anonymity. If we cannot ship a fix within 90 days we will publish a coordinated advisory documenting the issue and any mitigations available to users.

## Out-of-band

If you cannot reach `security@tesseraai.io`, you can DM `@govpun1-web` on GitHub for a fallback channel. Please do not file public issues for unpatched vulnerabilities.

Tessera is operated by Fintechagency OÜ, Tallinn, Estonia (registry 16638667).
