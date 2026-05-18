# Tessera SDK

> **Drop-in LLM cost optimization.** One line patches your existing OpenAI, Anthropic, Mistral, Groq, or Cohere client to route through Tessera's substrate proxy. Tessera **auto-routes** to cheaper-equivalent models, **auto-caches** repeated prompts, **auto-compresses** context, and **auto-batches** eligible requests. Every request is measured for cost delta — you pay only on measured savings.

[![PyPI](https://img.shields.io/pypi/v/tessera-llm-proxy.svg?label=PyPI)](https://pypi.org/project/tessera-llm-proxy/)
[![npm](https://img.shields.io/npm/v/@tessera-llm/sdk.svg?label=npm)](https://www.npmjs.com/package/@tessera-llm/sdk)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Free Dev tier: 60M tokens / month · no card required.** Get a key at [tesseraai.io/dev](https://tesseraai.io/dev) → 30-second signup → instant API key + magic-link dashboard access.

---

## 30-second curl test

```bash
curl https://api.tesseraai.io/v1/openai/chat/completions \
  -H "X-Tessera-Key: tk_<your-free-key>" \
  -H "Authorization: Bearer sk-<your-openai-key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello"}]}'

# Response shape = plain OpenAI. Behind the scenes: route + cache + compress + batch.
# Savings counter ticks live at ledger.tesseraai.io/portal.
```

---

## Install

| Language | Install |
|---|---|
| Python | `pip install tessera-llm-proxy` |
| Node / TypeScript | `npm install @tessera-llm/sdk` |

## One-line integration

### Python

```python
import tessera
tessera.activate("tk_your_tessera_key")

# Existing code runs unchanged. Any openai.OpenAI(), anthropic.Anthropic(),
# mistralai.Mistral(), groq.Groq(), cohere.Client() constructed AFTER this
# call routes through Tessera transparently. Your provider keys stay in
# the environment as usual.
```

### Node / TypeScript

```ts
import { activate } from "@tessera-llm/sdk";
activate("tk_your_tessera_key");

// Same shape: new OpenAI(), new Anthropic(), new Mistral(), etc. — all
// patched at load time. Bring-your-own provider keys.
```

---

## How it works (60 seconds)

1. **Get a free API key** — email + ToS at [ledger.tesseraai.io/signup-dev](https://ledger.tesseraai.io/signup-dev). You receive a `tk_` key shown once + magic link for dashboard access.
2. **Install the SDK** — `pip install tessera-llm-proxy` or `npm install @tessera-llm/sdk`.
3. **One line** — `tessera.activate("tk_…")` (Python) or `activate("tk_…")` (Node).
4. **Watch the counter** — tokens used + savings number tick live on [ledger.tesseraai.io/portal](https://ledger.tesseraai.io/portal).

Provider keys (your OpenAI `sk-…`, Anthropic `sk-ant-…`, etc.) stay in your environment. Tessera forwards them upstream untouched. We never store your prompts or completions — only token counts and cost deltas.

---

## What Tessera does to each request

| Mechanic | What it does | Effect |
|---|---|---|
| **Auto-route** | Swap requested model for a cheaper-equivalent in the same family (e.g. gpt-4o → gpt-4o-mini when quality canary score holds ≥ 0.95) | 30–95% input/output cost reduction |
| **Auto-cache** | Exact-match KV cache + semantic-similarity cache (≥0.95 cosine) for repeated prompts | Up to 100% on cache hits |
| **Auto-compress** | Whitespace + structural normalization preserving code fences, JSON ranges, semantic intent | 5–15% prompt size reduction |
| **Auto-batch** | Route async-tolerant calls to provider Batch APIs (OpenAI Batch = 50% off, Anthropic Message Batches = 50% off) | 50% on batch-eligible traffic |
| **Output-length predictor** | Inject p90-based `max_tokens` ceiling when historical truncation rate < 2% | 10–30% output token reduction |
| **Prompt cache** | Native prompt-cache headers for OpenAI / Anthropic / Google (90% off cached tokens) | 5–25× on cached prefixes |
| **Context pruning** | Conversation + RAG-block aware prune when message count > 12 OR body > 32 KB | 10–40% prompt token reduction |

Every mechanic is per-workload opt-in. Quality SLA: auto-disable + 10% fee credit if a workload's canary mean-score drops below 0.95 for 3 consecutive days.

---

## Pricing

| | **Free Dev** | **Production** |
|---|---|---|
| Token throughput | 60M / month | Unlimited |
| Rate limit | 10 req / min | 60 req / min |
| Performance fee | $0 | **20%** of measured savings · $0 if none |
| Balance management | — | Stripe top-ups ($100 min) |
| Monthly Reading PDF | — | Audit-grade ledger |
| Anomaly response | Observe only | Tier 1 throttle + Tier 2 halt |
| Team seats | — | Up to 5 |

**Zero savings = zero fee.** If our optimization doesn't save you anything in a period, you pay nothing for that period. **Kill-switch** in the portal pauses optimization any time — traffic still flows passthrough.

Upgrade flow: [ledger.tesseraai.io/portal/upgrade](https://ledger.tesseraai.io/portal/upgrade) · Full terms: [tesseraai.io/terms](https://tesseraai.io/terms).

---

## Supported providers

| Provider | Tessera route |
|---|---|
| OpenAI | `https://api.tesseraai.io/v1/openai` |
| Anthropic | `https://api.tesseraai.io/v1/anthropic` |
| Google (Gemini AI Studio) | `https://api.tesseraai.io/v1/google` |
| xAI | `https://api.tesseraai.io/v1/xai` |
| Cohere | `https://api.tesseraai.io/v1/cohere` |
| Mistral | `https://api.tesseraai.io/v1/mistral` |
| DeepSeek | `https://api.tesseraai.io/v1/deepseek` |
| Groq | `https://api.tesseraai.io/v1/groq` |
| Together AI | `https://api.tesseraai.io/v1/together` |
| Fireworks AI | `https://api.tesseraai.io/v1/fireworks` |
| OpenRouter | `https://api.tesseraai.io/v1/openrouter` |
| Perplexity | `https://api.tesseraai.io/v1/perplexity` |
| Cerebras | `https://api.tesseraai.io/v1/cerebras` |

AWS Bedrock, Azure OpenAI, Vertex AI: coming Q3 2026.

---

## Compared to observability tools

| | **Tessera** | Helicone / Langfuse / Portkey |
|---|---|---|
| Position | Substrate proxy in request path | Observability sidecar |
| Optimization | **Does it** (route, cache, compress, batch in real time) | Shows charts, no real-time mutation |
| Engineer effort | Two headers, that's it | Set up tracing + dashboards |
| Billing model | 20% of *measured* savings | Per-seat / per-event |
| Co-exists | Yes — they observe, we optimize | — |

---

## Frameworks & examples

The [examples/](./examples/) directory has runnable snippets:

- [`openai-wrap.py`](./examples/openai-wrap.py) — OpenAI client (Python)
- [`openai-wrap.ts`](./examples/openai-wrap.ts) — OpenAI client (Node)
- [`anthropic-wrap.py`](./examples/anthropic-wrap.py) — Anthropic client
- [`langchain-wrap.py`](./examples/langchain-wrap.py) — LangChain (no adapter needed — the activation patches the underlying SDK)
- [`direct-provider.py`](./examples/direct-provider.py) — DeepSeek / Together / Fireworks / etc. via OpenAI-compat URL

Works transparently with LangChain, LlamaIndex, CrewAI, AutoGen, Mastra, Pydantic AI, Vercel AI SDK — anything that calls the underlying provider SDK constructors.

---

## Documentation

- **Python SDK:** [./python/README.md](./python/README.md)
- **Node SDK:** [./node/README.md](./node/README.md)
- **Architecture:** [tesseraai.io/how-it-works](https://tesseraai.io/how-it-works)
- **Quality SLA:** [tesseraai.io/security](https://tesseraai.io/security)
- **API reference:** [docs.tesseraai.io](https://docs.tesseraai.io)

---

## Contributing

PRs welcome for new examples, framework adapters, type-stub improvements, and bug fixes. See [CONTRIBUTING.md](./CONTRIBUTING.md).

- **Bug reports:** [github.com/tessera-llm/sdk/issues](https://github.com/tessera-llm/sdk/issues)
- **Security:** [security@tesseraai.io](mailto:security@tesseraai.io)

---

## License

Apache-2.0. See [LICENSE](./LICENSE).

---

## About Tessera

Tessera is the Optimize Layer for LLM cost. A thin proxy in your request path that **measures savings honestly** and only charges when we actually saved you money. Built and operated by Fintechagency OÜ (Estonia, registry code 16638667).

- Landing: [tesseraai.io](https://tesseraai.io)
- Developer entry: [tesseraai.io/dev](https://tesseraai.io/dev)
- Dashboard: [ledger.tesseraai.io](https://ledger.tesseraai.io)
- Founder: [founder@tesseraai.io](mailto:founder@tesseraai.io)
