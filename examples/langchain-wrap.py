"""
langchain-wrap.py — Tessera SDK with LangChain's OpenAI integration.

LangChain wraps the OpenAI SDK constructor under the hood, so Tessera's
patch transparently catches the underlying calls — no LangChain-specific
adapter needed.

Prerequisites:
    pip install tessera-llm-proxy langchain-openai
    export TESSERA_KEY=tk_...
    export OPENAI_API_KEY=sk-...

Run:
    python langchain-wrap.py
"""

import tessera
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def main() -> None:
    tessera.activate()

    chat = ChatOpenAI(model="gpt-4o-mini", max_tokens=200)

    response = chat.invoke([HumanMessage(content="What is auto-routing in 2 sentences?")])
    print(response.content)


if __name__ == "__main__":
    main()
