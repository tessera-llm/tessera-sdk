# @tessera-llm/tessera-sdk

[![npm version](https://img.shields.io/npm/v/@tessera-llm/tessera-sdk.svg)](https://www.npmjs.com/package/@tessera-llm/tessera-sdk)
[![Node](https://img.shields.io/node/v/@tessera-llm/tessera-sdk.svg)](https://www.npmjs.com/package/@tessera-llm/tessera-sdk)

**Drop-in cost optimization for LLM applications.** One line of code patches your existing OpenAI / Anthropic / Mistral / DeepSeek / Groq / Together / Fireworks / OpenRouter / Perplexity / Cerebras / xAI client to route through Tessera's measurement + auto-optimize proxy. You keep your provider account and keys; we route + cache + compress and measure savings on every request.

> Free Dev tier: **60M tokens / month · no card required · no fee until you upgrade.** Get your free key at [tesseraai.io/dev](https://tesseraai.io/dev).

## Get a free API key

→ **[Get free key](https://ledger.tesseraai.io/signup-dev)** (email + ToS, 30 seconds, no card)

After signup you get:
- Your `tk_` API key (shown once)
- A magic-link for the [dashboard](https://ledger.tesseraai.io/portal) — see your token counter + savings counter live
- 60M tokens/month at 30 req/min — generous for hobby + side projects

## Install

```bash
npm install @tessera-llm/tessera-sdk
# or: pnpm add @tessera-llm/tessera-sdk
# or: yarn add @tessera-llm/tessera-sdk
```

## One-line setup

Drop this at the top of your application's entry point (`server.ts`, `app.ts`, `index.ts`, wherever your app boots — before any LLM SDK client is constructed):

```ts
import { activate } from "@tessera-llm/tessera-sdk";

activate("tk_your_tessera_key");
```

That's it. Your existing code runs unchanged — `new OpenAI()`, `new Anthropic()`, and other supported SDK constructors are transparently patched to route through Tessera. Your provider keys (OpenAI `sk-...`, Anthropic `sk-ant-...`, etc.) stay in your environment as before; Tessera forwards them upstream untouched.

### Environment variable form

If you'd rather not put the key in code:

```bash
export TESSERA_KEY=tk_your_tessera_key
```

```ts
import { activate } from "@tessera-llm/tessera-sdk";
activate(); // reads TESSERA_KEY from process.env
```

## What gets patched

Calling `activate(...)` patches the following SDKs at load time (each is opt-in: only patched if the library is installed as a peer dependency):

| SDK | Tessera route |
| --- | --- |
| `openai` | `https://api.tesseraai.io/v1/openai` |
| `@anthropic-ai/sdk` | `https://api.tesseraai.io/v1/anthropic` |
| `@mistralai/mistralai` | `https://api.tesseraai.io/v1/mistral` |
| `groq-sdk` | `https://api.tesseraai.io/v1/groq` |
| `cohere-ai` | `https://api.tesseraai.io/v1/cohere` *(Wave 2)* |

If you use a framework that wraps these SDKs (LangChain.js, LlamaIndex.TS, Vercel AI SDK, Mastra, etc.), the patch applies transparently because those frameworks call the underlying SDK constructors which are what we patched.

## Direct provider URLs

If you call providers that aren't covered by an official Node SDK (DeepSeek, Together, Fireworks, OpenRouter, Perplexity, Cerebras, xAI), construct an `OpenAI` client manually with the matching Tessera URL:

```ts
import OpenAI from "openai";
import { url, headers } from "@tessera-llm/tessera-sdk";

// DeepSeek via Tessera
const client = new OpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY,
  baseURL: url("deepseek"),       // → https://api.tesseraai.io/v1/deepseek
  defaultHeaders: headers(),
});

// Same pattern for: together, fireworks, openrouter, perplexity, cerebras, groq, xai
```

`url(provider)` and `headers()` are pure helpers — no globals, no patching. Use them when you want explicit, traceable wiring.

## Verification

```ts
import { activate, isActive, status } from "@tessera-llm/tessera-sdk";

activate("tk_...");

console.log(isActive());  // → true
console.log(status());
// → { active: true, providersPatched: ['openai', 'anthropic'], proxyBase: 'https://api.tesseraai.io/v1', featureTag: null }
```

## Deactivation

To restore the original SDK constructors (e.g. in test teardown):

```ts
import { deactivate } from "@tessera-llm/tessera-sdk";
deactivate();
```

## Configuration

```ts
activate("tk_...", {
  proxyBase: "https://api.tesseraai.io/v1",  // default; override for staging/dev
  featureTag: "checkout-summarizer",         // attaches X-Tessera-Feature-Tag to every request
});
```

`featureTag` lets you split savings reporting per workload (e.g. one tag per logical feature in your app). You can also set per-request tags by passing `extra_body: { tessera_feature_tag: "..." }` on individual SDK calls.

## Pricing

Two tiers:

| | **Free Dev** | **Production** |
|---|---|---|
| Token throughput | 60M / month | Unlimited |
| Rate limit | 30 req / min | 60 req / min |
| Performance fee | $0 | **20%** of measured savings · $0 if none |
| Balance management | — | Stripe top-ups ($100 min) |
| Monthly Reading PDF | — | Audit-grade ledger |
| Anomaly response | Observe only | Tier 1 throttle + Tier 2 halt |
| Team seats | — | Up to 5 |

**Zero savings = zero fee.** Even on Production, if our optimization doesn't save you anything in a period, you pay nothing for that period.

**Kill-switch** available anytime from your portal — pauses optimization, traffic still flows passthrough.

Full terms: <https://tesseraai.io/terms> · Upgrade flow: <https://ledger.tesseraai.io/portal/upgrade>

## License

Apache-2.0
