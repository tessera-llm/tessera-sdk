# Tessera SDK — drop-in LLM cost optimization

**Cut 20–60% off your OpenAI / Anthropic / Gemini / Mistral bill with one line of code.** Tessera is a substrate proxy that sits in your LLM request path, auto-routes to cheaper-equivalent models, caches repeated prompts, compresses context, and batches eligible calls. Every request is measured for cost delta. **You pay 20% only on measured savings — zero savings, zero fee.**

[![PyPI](https://img.shields.io/pypi/v/tessera-llm-proxy.svg?label=PyPI)](https://pypi.org/project/tessera-llm-proxy/)
[![npm](https://img.shields.io/npm/v/@tessera-llm/sdk.svg?label=npm)](https://www.npmjs.com/package/@tessera-llm/sdk)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Free Dev tier: 60M tokens / month · no card required · 30-second signup at [tesseraai.io/dev](https://tesseraai.io/dev).**

---

## Who this is for

- **AI-native SaaS** spending $5k+/month on OpenAI / Anthropic / Gemini and wanting that bill cut without re-architecting.
- **Vertical AI agents** (sales, support, voice, customer success) where margin compresses as call volume scales.
- **Engineering teams** who want an honest cost reduction layer — not yet another observability dashboard.

**Not for:** hobby projects under $500/month bills (the free tier is enough, no upgrade signal). Air-gapped on-prem deployments (we're a hosted proxy by design).

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

## Worked example — what 20% of savings looks like

A customer-support AI agent runs on `gpt-4o` with high prompt repetition (FAQ-style queries). 1.2B tokens/month at OpenAI list prices = **$24,000/month bill** at the start of the period.

After enabling Tessera (no code change beyond one-line activate):

| Stage | Cost / month | Savings |
|---|---:|---:|
| Baseline (OpenAI direct) | $24,000 | — |
| + auto-cache (35% hit rate on FAQ prefix) | $15,600 | $8,400 |
| + auto-route (gpt-4o → gpt-4o-mini where quality canary holds) | $11,520 | $4,080 |
| + prompt cache (90% off cached system prefix) | $9,950 | $1,570 |
| + context pruning (RAG trim) | $9,400 | $550 |
| **Tessera-optimized total** | **$9,400** | **$14,600 / month** |
| **Tessera fee (20% of savings)** | $2,920 | — |
| **Customer net** | **$12,320** | **$11,680 saved / month** |

Quality canary mean-score held at 0.96 across all stages (floor 0.95) — if it had dropped, M1 auto-route would have rolled back and the customer received a 10% SLA credit on the affected days. **Numbers vary by workload shape.** Run your own workload free for 60M tokens to measure your actual delta.

---

## What Tessera does to each request

Seven mechanics, eval-gated. Each is per-workload opt-in. Stage 3 mutex caps content-mutating mechanics at one per request to bound quality risk.

| Mechanic | What it does | Effect |
|---|---|---|
| **Auto-route (M1)** | Swap requested model for a cheaper-equivalent in the same family (e.g. `gpt-4o → gpt-4o-mini`) when quality canary holds ≥ 0.95 | 30–95% cost reduction on routed calls |
| **Auto-cache (M2)** | Exact-match KV cache for repeated prompts within TTL | Up to 100% on cache hits |
| **Auto-compress (M3)** | Whitespace + structural normalization, preserving code fences + JSON ranges + semantic intent. Per-role opt-in (compress system prompts and/or user turns independently) | 5–15% prompt size reduction |
| **Semantic cache (M5)** | Embedding-based similarity cache (cosine ≥ 0.95) for near-duplicate prompts | Up to 100% on semantic hits |
| **Prompt cache (M6)** | Native provider prompt-cache headers (OpenAI / Anthropic / Google) | 5–25× on cached prefixes |
| **Context pruning (M7)** | Conversation + RAG-block aware prune when message count > 12 OR body > 32 KB | 10–40% prompt token reduction |
| **Structured output (M8)** | Inject `response_format=json_schema` (strict mode) or `json_object` (auto mode) when an expected_schema is set | 10–35% output cost cut on JSON workloads |
| **Auto-batch (M10)** | Route async-tolerant calls to provider Batch APIs (OpenAI Batch / Anthropic Message Batches = 50% off) | 50% on batch-eligible traffic |

---

## Quality SLA — auto-rollback + 10% credit

A canary runs your workload at 10% sample rate against the baseline model, scored by a [promptfoo](https://promptfoo.dev) eval set you can define. If a workload's stack mean-score drops below 0.95 for 3 consecutive days with at least 30 samples per stack:

1. The specific stack (e.g. `m1+m7`) auto-disables. `m1` alone and `m7` alone stay live — surgical rollback, not nuclear.
2. A 10% credit on the last 3 days' fees attributable to that stack lands on your prepaid balance automatically.
3. An audit_event records the breach + credit + reactivation timeline in your `/portal/audit` ledger.

You can also flip the global kill-switch in `/portal/settings` at any time — traffic continues flowing as passthrough, just with no mutation.

---

## How it works (60 seconds)

1. **Get a free API key** — email + ToS at [ledger.tesseraai.io/signup-dev](https://ledger.tesseraai.io/signup-dev). You receive a `tk_` key shown once + magic link for dashboard access.
2. **Install the SDK** — `pip install tessera-llm-proxy` or `npm install @tessera-llm/sdk`.
3. **One line** — `tessera.activate("tk_…")` (Python) or `activate("tk_…")` (Node).
4. **Watch the counter** — tokens used + savings number tick live on [ledger.tesseraai.io/portal](https://ledger.tesseraai.io/portal).

Provider keys (your OpenAI `sk-…`, Anthropic `sk-ant-…`, etc.) stay in your environment. Tessera forwards them upstream untouched. We never store your prompts or completions — only token counts and cost deltas. See the [data privacy FAQ](#faq) below.

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

## FAQ

### Do you store my prompts or completions?

No. The proxy logs token counts, model identifiers, cost deltas, and request_id — never the prompt or response bodies. The exact-match cache stores hashed prompts (sha256) for lookup keys; the semantic cache stores prompt embeddings (irreversible). [Full data handling](https://tesseraai.io/security).

### What's the latency overhead?

Tessera adds ~15–40 ms p50 on cache-miss paths (one extra TLS hop to Cloudflare edge). On cache hits, **latency drops** (no upstream call). Auto-batch trades latency for cost — opt-in per workload only.

### How do you measure quality without seeing prompts?

You provide a [promptfoo](https://promptfoo.dev) golden set (5–50 prompts representative of your workload). The canary cron runs your workload's mechanics_stack at 10% sample rate against the baseline model, scored by your eval set, daily. The aggregate mean_score per stack drives the quality SLA. You retain full control of the eval set — we just run it.

### Where are you in your SOC 2 journey?

We're targeting SOC 2 Type 1 by Q3 2026. Current security posture: zero prompt/response storage at-rest, customer Authorization keys at-rest-encrypted via Supabase Vault (XChaCha20-Poly1305-IETF under the hood), RLS isolation per tenant, audit trail with cryptographic provenance via pricing_catalog snapshot ids. [Security page](https://tesseraai.io/security).

### Why open-source the SDK if the proxy is closed?

The SDK is the integration surface — the part you ship in your binary. Apache-2.0 lets you fork, audit, vendor in, and prove to your security review that nothing exotic happens client-side. The proxy at `api.tesseraai.io` is closed because the mechanic implementations are the asymmetric IP. The wire format is open: any HTTPS client speaking OpenAI / Anthropic / Google shapes can use Tessera without our SDK.

### How is the savings number computed — couldn't you inflate it?

Each request emits two cost figures: `original_cost_usd` (priced at the **requested** model's catalog rate) and `actual_cost_usd` (priced at the **actual** model after routing + cache hits + provider discounts). Both rates are pinned to a [`pricing_catalog`](https://tesseraai.io/how-it-works) snapshot version id captured at the request — immutable, with multi-source verification (LiteLLM + tokencost + OpenRouter API + direct provider docs, confidence-scored). Mid-contract price changes don't retroactively alter past savings. The audit ledger is yours to export.

### Can I see what mechanics fired on a specific request?

Yes. `/portal/audit` shows a chip strip per request (`m1`, `m2`, `m3`, etc.). Each request_id is searchable by `feature_tag` / `customer_tag` headers you can set per call. Full mechanic reference at [tesseraai.io/how-it-works](https://tesseraai.io/how-it-works).

### What if I want to opt out of a specific mechanic?

Per workload, in `/portal/settings`: toggle any of the seven mechanics on/off. Or use the request-level header `x-tessera-do-not-optimize: true` for one-off passthrough. Kill-switch in `/portal/billing` pauses everything across all workloads.

---

## Documentation

- **Python SDK:** [./python/README.md](./python/README.md)
- **Node SDK:** [./node/README.md](./node/README.md)
- **Architecture:** [tesseraai.io/how-it-works](https://tesseraai.io/how-it-works)
- **Quality SLA:** [tesseraai.io/security](https://tesseraai.io/security)
- **Mechanic reference:** [tesseraai.io/how-it-works](https://tesseraai.io/how-it-works)
- **Engineering blog:** [tesseraai.io/blog](https://tesseraai.io/blog)

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
