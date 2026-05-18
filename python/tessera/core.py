"""Tessera SDK core — global activation + per-provider patchers.

`activate()` walks a registry of provider-specific patchers. Each patcher is
opt-in: only fires if the corresponding SDK is importable. So a Python process
that has only `openai` installed will see `openai` patched and `anthropic`
silently skipped.

Patchers wrap the SDK's primary client constructor(s). After the wrap, every
new client instance created in the process has its `base_url` pointed at the
Tessera proxy + `X-Tessera-Key` injected into default headers, while the
caller's existing provider key (e.g. `sk-...`) stays untouched and flows
upstream as before.

This is intentionally a **global side-effect** per founder direction — same
shape as `cloudflare.activate()` or `sentry.init()`. Reversal via
`deactivate()` for test teardown.
"""

from __future__ import annotations

import dataclasses
import importlib
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("tessera")

DEFAULT_PROXY_BASE = "https://api.tesseraai.io/v1"

_state: Dict[str, Any] = {
    "active": False,
    "key": None,
    "proxy_base": DEFAULT_PROXY_BASE,
    "feature_tag": None,
    "patched": [],  # list of (provider_name, restore_callable)
}


@dataclasses.dataclass
class ProxyStatus:
    """Current state of the Tessera SDK patch."""

    active: bool
    providers_patched: List[str]
    proxy_base: str
    feature_tag: Optional[str]


def url(provider: str) -> str:
    """Return the Tessera proxy URL for ``provider``.

    Pure helper — no globals required. Use when wiring an SDK client manually
    (e.g. for providers without an official Python SDK such as DeepSeek,
    Together, Fireworks, OpenRouter, Perplexity, Cerebras, xAI).
    """
    base = _state.get("proxy_base") or DEFAULT_PROXY_BASE
    return f"{base.rstrip('/')}/{provider.strip('/')}"


def headers(key: Optional[str] = None) -> Dict[str, str]:
    """Return the headers required to authenticate against Tessera.

    Reads the activated key by default; pass ``key`` explicitly to override.
    Use alongside :func:`url` for manual SDK wiring.
    """
    resolved_key = key or _state.get("key") or os.environ.get("TESSERA_KEY")
    if not resolved_key:
        raise RuntimeError(
            "Tessera key not set. Call `tessera.activate('tk_...')` first or "
            "pass key= to tessera.headers()."
        )
    result = {"X-Tessera-Key": resolved_key}
    tag = _state.get("feature_tag")
    if tag:
        result["X-Tessera-Feature-Tag"] = tag
    return result


def is_active() -> bool:
    """True if :func:`activate` has been called and patches are installed."""
    return bool(_state.get("active"))


def status() -> ProxyStatus:
    """Snapshot the current SDK state — useful in health checks + logging."""
    return ProxyStatus(
        active=bool(_state.get("active")),
        providers_patched=[name for name, _ in _state.get("patched", [])],
        proxy_base=_state.get("proxy_base") or DEFAULT_PROXY_BASE,
        feature_tag=_state.get("feature_tag"),
    )


def activate(
    key: Optional[str] = None,
    *,
    proxy_base: Optional[str] = None,
    feature_tag: Optional[str] = None,
) -> ProxyStatus:
    """Install Tessera patches globally.

    :param key: Tessera API key (``tk_...``). Falls back to ``TESSERA_KEY``
        environment variable when omitted.
    :param proxy_base: Override the proxy origin. Default
        ``https://api.tesseraai.io/v1``. Used by Tessera staff for staging.
    :param feature_tag: Attach a default ``X-Tessera-Feature-Tag`` header to
        every patched request — useful for per-workload attribution.
    :returns: :class:`ProxyStatus` with the current state.
    :raises RuntimeError: If no key is provided either argument-side or via
        the environment variable.
    """
    resolved_key = key or os.environ.get("TESSERA_KEY")
    if not resolved_key:
        raise RuntimeError(
            "Tessera key not provided. Pass key= to tessera.activate() or set "
            "TESSERA_KEY environment variable."
        )

    if _state["active"]:
        # Re-activating with new args: deactivate first so we can re-patch with
        # the new state cleanly.
        deactivate()

    _state["key"] = resolved_key
    _state["proxy_base"] = (proxy_base or DEFAULT_PROXY_BASE).rstrip("/")
    _state["feature_tag"] = feature_tag
    _state["active"] = True
    _state["patched"] = []

    for patcher in _PATCHERS:
        try:
            restore = patcher()
            if restore is not None:
                _state["patched"].append((patcher.__name__.replace("_patch_", ""), restore))
        except Exception as err:  # noqa: BLE001 — best-effort patching
            logger.warning(
                "tessera: failed to patch %s: %s",
                patcher.__name__,
                err,
            )

    return status()


def deactivate() -> None:
    """Reverse all patches installed by :func:`activate`.

    SDK constructors are restored to their original values. Safe to call when
    Tessera is not active — becomes a no-op.
    """
    for _provider, restore in reversed(_state.get("patched", [])):
        try:
            restore()
        except Exception as err:  # noqa: BLE001
            logger.warning("tessera: failed to restore patch: %s", err)
    _state["active"] = False
    _state["patched"] = []
    _state["key"] = None
    _state["feature_tag"] = None


# ─── per-provider patchers ──────────────────────────────────────────────────


def _safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def _wrap_constructor(
    cls: type,
    *,
    base_url_attr: str = "base_url",
    headers_attr: str = "default_headers",
    proxy_path: str,
) -> Callable[[], None]:
    """Wrap ``cls.__init__`` so newly-constructed instances route via Tessera.

    Returns a restore callable that undoes the wrap.
    """
    original_init = cls.__init__
    proxy_url = url(proxy_path)

    def patched_init(self: Any, *args: Any, **kwargs: Any) -> None:
        # Don't override an explicit base_url override — caller wins.
        if base_url_attr not in kwargs:
            kwargs[base_url_attr] = proxy_url
        # Merge default headers — preserve any caller-provided headers.
        merged_headers: Dict[str, str] = dict(kwargs.get(headers_attr) or {})
        for header_key, header_value in headers().items():
            merged_headers.setdefault(header_key, header_value)
        kwargs[headers_attr] = merged_headers
        original_init(self, *args, **kwargs)

    cls.__init__ = patched_init  # type: ignore[method-assign]

    def restore() -> None:
        cls.__init__ = original_init  # type: ignore[method-assign]

    return restore


def _patch_openai() -> Optional[Callable[[], None]]:
    mod = _safe_import("openai")
    if mod is None:
        return None
    restorers: List[Callable[[], None]] = []
    for class_name in ("OpenAI", "AsyncOpenAI"):
        cls = getattr(mod, class_name, None)
        if cls is None:
            continue
        restorers.append(
            _wrap_constructor(cls, proxy_path="openai")
        )

    def restore_all() -> None:
        for r in restorers:
            r()

    return restore_all if restorers else None


def _patch_anthropic() -> Optional[Callable[[], None]]:
    mod = _safe_import("anthropic")
    if mod is None:
        return None
    restorers: List[Callable[[], None]] = []
    for class_name in ("Anthropic", "AsyncAnthropic"):
        cls = getattr(mod, class_name, None)
        if cls is None:
            continue
        restorers.append(
            _wrap_constructor(cls, proxy_path="anthropic")
        )

    def restore_all() -> None:
        for r in restorers:
            r()

    return restore_all if restorers else None


def _patch_mistral() -> Optional[Callable[[], None]]:
    # Newer Mistral SDK (>=1.0) exposes class `Mistral`; legacy uses
    # `MistralClient`. Patch whichever is present.
    mod = _safe_import("mistralai")
    if mod is None:
        return None
    restorers: List[Callable[[], None]] = []
    for class_name in ("Mistral", "MistralClient", "AsyncMistral"):
        cls = getattr(mod, class_name, None)
        if cls is None:
            continue
        # Mistral SDK uses `server_url` rather than `base_url`
        restorers.append(
            _wrap_constructor(
                cls,
                base_url_attr="server_url",
                headers_attr="default_headers",
                proxy_path="mistral",
            )
        )

    def restore_all() -> None:
        for r in restorers:
            r()

    return restore_all if restorers else None


def _patch_groq() -> Optional[Callable[[], None]]:
    mod = _safe_import("groq")
    if mod is None:
        return None
    restorers: List[Callable[[], None]] = []
    for class_name in ("Groq", "AsyncGroq"):
        cls = getattr(mod, class_name, None)
        if cls is None:
            continue
        restorers.append(
            _wrap_constructor(cls, proxy_path="groq")
        )

    def restore_all() -> None:
        for r in restorers:
            r()

    return restore_all if restorers else None


def _patch_cohere() -> Optional[Callable[[], None]]:
    mod = _safe_import("cohere")
    if mod is None:
        return None
    restorers: List[Callable[[], None]] = []
    # Cohere v5+ SDK class names — patch whichever exist.
    for class_name in ("Client", "ClientV2", "AsyncClient", "AsyncClientV2"):
        cls = getattr(mod, class_name, None)
        if cls is None:
            continue
        # Cohere uses `base_url` keyword
        restorers.append(
            _wrap_constructor(cls, proxy_path="cohere")
        )

    def restore_all() -> None:
        for r in restorers:
            r()

    return restore_all if restorers else None


_PATCHERS: Tuple[Callable[[], Optional[Callable[[], None]]], ...] = (
    _patch_openai,
    _patch_anthropic,
    _patch_mistral,
    _patch_groq,
    _patch_cohere,
)
