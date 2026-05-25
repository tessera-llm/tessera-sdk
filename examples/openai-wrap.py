"""
openai-wrap.py — Tessera SDK quick start with the OpenAI Python client.

Prerequisites:
    pip install tessera-llm-proxy openai
    export TESSERA_KEY=tk_...           # from https://tesseraai.io/dev
    export OPENAI_API_KEY=sk-...        # your existing OpenAI key

Run:
    python openai-wrap.py

Expected behavior:
    1. First call: forwards to api.tesseraai.io/v1/openai/chat/completions
    2. Worker measures input/output token cost, emits OptimizeEvent
    3. Dashboard /portal/overview counter updates within seconds
    4. Same prompt within 7 days returns from cache (auto-cache mechanic)
"""

import tessera
from openai import OpenAI


def main() -> None:
    # One line patches every subsequent OpenAI() constructor in the process.
    tessera.activate()  # reads TESSERA_KEY from env

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a terse expert."},
            {"role": "user", "content": "Explain prompt caching in 2 sentences."},
        ],
        max_tokens=200,
    )

    print(response.choices[0].message.content)
    print()
    print(f"tokens: in={response.usage.prompt_tokens} out={response.usage.completion_tokens}")
    print()
    print("Open https://ledger.tesseraai.io/portal to see savings + counter live.")


if __name__ == "__main__":
    main()
