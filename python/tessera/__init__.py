"""Tessera Optimize Layer — drop-in cost optimization for LLM SDKs.

One line of code patches OpenAI / Anthropic / Mistral / Groq / Cohere client
constructors so requests route through Tessera's measurement + auto-optimize
proxy. Your existing application code runs unchanged.

Typical use::

    import tessera
    tessera.activate("tk_your_tessera_key")

    # Now any existing OpenAI/Anthropic/etc client created in this Python
    # process will transparently forward through Tessera. No further code
    # changes required.

For SDKs we don't auto-patch (DeepSeek/Together/Fireworks/OpenRouter/etc),
use ``tessera.url(provider)`` + ``tessera.headers()`` to wire an
``openai.OpenAI`` client manually.

Locked 2026-05-17 — γ-mode integration per founder direction
("Cloudflare-стиль: дай ключ, остальное мы делаем").
"""

from __future__ import annotations

from .core import (
    ProxyStatus,
    activate,
    deactivate,
    headers,
    is_active,
    status,
    url,
)

__version__ = "0.1.0"

__all__ = [
    "activate",
    "deactivate",
    "headers",
    "is_active",
    "ProxyStatus",
    "status",
    "url",
    "__version__",
]
