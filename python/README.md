# tessera-llm-proxy

[![PyPI version](https://img.shields.io/pypi/v/tessera-llm-proxy.svg)](https://pypi.org/project/tessera-llm-proxy/)
[![Python](https://img.shields.io/pypi/pyversions/tessera-llm-proxy.svg)](https://pypi.org/project/tessera-llm-proxy/)

**Drop-in cost optimization for LLM applications.** One line of code patches your existing OpenAI / Anthropic / Mistral / DeepSeek / Groq / Together / Fireworks / OpenRouter / Perplexity / Cerebras / xAI client to route through Tessera's measurement + auto-optimize proxy. You keep your provider account and keys; we route + cache + compress and measure savings on every request.

> Free Sandbox tier: **60M tokens / month · no card required · no fee until you upgrade.** Get your free key at [tesseraai.io/dev](https://tesseraai.io/dev).

## Get a free API key

→ **[Get free key](https://tesseraai.io/dev)** (email + ToS, 30 seconds, no card)

After signup you get:
- Your `tk_` API key (shown once)
- A magic-link for the [dashboard](https://ledger.tesseraai.io/portal) — see your token counter + savings counter live
- 60M tokens/month at 30 req/min — generous for hobby + side projects

## Install

```bash
pip install tessera-llm-proxy
```

## One-line setup

Drop this at the top of your application's entry point (`main.py`, `app.py`, `manage.py`, wherever your app boots):

```python
import tessera
tessera.activate("tk_your_tessera_key")
```

That's it. Your existing code runs unchanged — `openai.OpenAI()`, `anthropic.Anthropic()`, `mistralai.Mistral()`, and other supported SDK constructors are transparently patched to route through Tessera. Your provider keys (OpenAI `sk-...`, Anthropic `sk-ant-...`, etc.) stay in your environment as before; Tessera forwards them upstream untouched.

### Environment variable form

If you'd rather not put the key in code:

```bash
export TESSERA_KEY=tk_your_tessera_key
```

```python
import tessera
tessera.activate()  # reads TESSERA_KEY from environment
```

## What gets patched

Calling `tessera.activate(...)` patches the following SDKs at import time (each is opt-in: only patched if the library is installed):

| SDK | Tessera route |
| --- | --- |
| `openai` (≥1.0) | `https://api.tesseraai.io/v1/openai` |
| `anthropic` | `https://api.tesseraai.io/v1/anthropic` |
| `mistralai` | `https://api.tesseraai.io/v1/mistral` |
| `cohere` | `https://api.tesseraai.io/v1/cohere` *(Wave 2)* |
| `groq` | `https://api.tesseraai.io/v1/groq` |

If you use a framework that wraps these SDKs (LangChain, LlamaIndex, CrewAI, AutoGen, Mastra, Pydantic AI, etc.), the patch applies transparently because those frameworks call the underlying SDK constructors which are what we patched.

## Direct provider URLs

If you call providers that aren't covered by an official Python SDK (DeepSeek, Together, Fireworks, OpenRouter, Perplexity, Cerebras, xAI), construct an `openai.OpenAI` client manually with the matching Tessera URL:

```python
from openai import OpenAI

# DeepSeek via Tessera
client = OpenAI(
    api_key="sk-deepseek-...",
    base_url=tessera.url("deepseek"),  # → https://api.tesseraai.io/v1/deepseek
    default_headers=tessera.headers(),
)

# Same pattern for: together, fireworks, openrouter, perplexity, cerebras, groq, xai
```

`tessera.url(provider)` and `tessera.headers()` are pure helpers — no globals, no patching. Use them when you want explicit, traceable wiring.

## Verification

```python
import tessera
tessera.activate("tk_...")

assert tessera.is_active(), "Tessera should be active after activate()"
print(tessera.status())  # → ProxyStatus(active=True, providers_patched=['openai', 'anthropic'], proxy_base='https://api.tesseraai.io/v1')
```

## Deactivation

To restore the original SDK constructors (e.g. in test teardown):

```python
tessera.deactivate()
```

## Configuration

```python
tessera.activate(
    key="tk_...",                              # or TESSERA_KEY env var
    proxy_base="https://api.tesseraai.io/v1",  # default; override for staging/dev
    feature_tag="checkout-summarizer",         # attaches to every request for per-feature attribution
)
```

`feature_tag` lets you split savings reporting per workload (e.g. one tag per logical feature in your app). You can also set per-request tags by passing `extra_body={"tessera_feature_tag": "..."}` on individual SDK calls.

## How the pricing works

- **Free Sandbox tier:** 60M tokens/month, no card required, $0 fee.
- **Production tier:** **20%** of measured savings, debited daily from a prepaid balance you control ($100 minimum top-up via Stripe).
- **Zero savings = zero fee.** If our optimization doesn't save you anything in a period, you pay nothing for that period.
- **Kill-switch** available anytime from your portal — pauses optimization, traffic still flows passthrough.

Full terms: <https://tesseraai.io/terms>

## License

Apache-2.0
