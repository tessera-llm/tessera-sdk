/**
 * openai-wrap.ts — Tessera SDK quick start with the OpenAI Node client.
 *
 * Prerequisites:
 *   npm install @tessera-llm/tessera-sdk openai
 *   export TESSERA_KEY=tk_...           # from https://ledger.tesseraai.io/signup-dev
 *   export OPENAI_API_KEY=sk-...        # your existing OpenAI key
 *
 * Run (with tsx):
 *   npx tsx openai-wrap.ts
 *
 * Expected behavior:
 *   1. First call: forwards to api.tesseraai.io/v1/openai/chat/completions
 *   2. Worker measures input/output token cost, emits OptimizeEvent
 *   3. Dashboard /portal/overview counter updates within seconds
 *   4. Same prompt within 7 days returns from cache (auto-cache mechanic)
 */

import { activate } from '@tessera-llm/tessera-sdk';
import OpenAI from 'openai';

async function main() {
  // One line patches every subsequent new OpenAI() constructor in the process.
  activate(); // reads TESSERA_KEY from process.env

  const client = new OpenAI();

  const response = await client.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are a terse expert.' },
      { role: 'user', content: 'Explain prompt caching in 2 sentences.' },
    ],
    max_tokens: 200,
  });

  console.log(response.choices[0].message.content);
  console.log();
  console.log(`tokens: in=${response.usage?.prompt_tokens} out=${response.usage?.completion_tokens}`);
  console.log();
  console.log('Open https://ledger.tesseraai.io/portal to see savings + counter live.');
}

main().catch(console.error);
