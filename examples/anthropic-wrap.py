"""
anthropic-wrap.py — Tessera SDK with the Anthropic Python client.

Prerequisites:
    pip install tessera-llm-proxy anthropic
    export TESSERA_KEY=tk_...
    export ANTHROPIC_API_KEY=sk-ant-...

Run:
    python anthropic-wrap.py
"""

import tessera
from anthropic import Anthropic


def main() -> None:
    tessera.activate()

    client = Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=300,
        messages=[
            {"role": "user", "content": "What is a substrate proxy in 2 sentences?"},
        ],
    )

    print(message.content[0].text)
    print()
    print(f"tokens: in={message.usage.input_tokens} out={message.usage.output_tokens}")


if __name__ == "__main__":
    main()
