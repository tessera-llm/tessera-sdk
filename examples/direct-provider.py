"""
direct-provider.py — Use Tessera with providers that don't ship an
official Python SDK (DeepSeek, Together, Fireworks, OpenRouter, Cerebras,
Perplexity, etc.).

These providers all expose OpenAI-compatible APIs, so use the OpenAI
client manually with the matching Tessera URL.

Prerequisites:
    pip install tessera-llm-proxy openai
    export TESSERA_KEY=tk_...
    export DEEPSEEK_API_KEY=...   # whichever provider you're using
"""

import os
import tessera
from openai import OpenAI


def main() -> None:
    # No activate() needed for this pattern — we explicitly wire the client.
    # Use tessera.url(provider) + tessera.headers() for the routing primitives.

    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=tessera.url("deepseek"),         # → https://api.tesseraai.io/v1/deepseek
        default_headers=tessera.headers(),
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Two-sentence elevator pitch for DeepSeek."}],
        max_tokens=200,
    )

    print(response.choices[0].message.content)
    print(f"tokens: in={response.usage.prompt_tokens} out={response.usage.completion_tokens}")

    # Same pattern works for: together, fireworks, openrouter, perplexity,
    # cerebras, groq, xai. Just change the url(provider) argument.


if __name__ == "__main__":
    main()
