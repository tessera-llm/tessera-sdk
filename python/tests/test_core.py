"""Tessera SDK core tests — unit-level (no network).

We don't have OpenAI/Anthropic installed in the test environment necessarily,
so tests focus on the pure helpers (url, headers, status, activate/deactivate
lifecycle) and use a stub class to verify the wrap behaviour without depending
on a specific provider SDK being importable.
"""

from __future__ import annotations

import os
import sys
import types

import pytest

import tessera
from tessera import core as tessera_core


@pytest.fixture(autouse=True)
def reset_state():
    """Ensure each test starts fresh."""
    tessera_core.deactivate()
    yield
    tessera_core.deactivate()


def test_default_proxy_base():
    assert tessera_core.DEFAULT_PROXY_BASE == "https://api.tesseraai.io/v1"


def test_url_helper():
    assert tessera.url("openai") == "https://api.tesseraai.io/v1/openai"
    assert tessera.url("anthropic") == "https://api.tesseraai.io/v1/anthropic"
    assert tessera.url("deepseek") == "https://api.tesseraai.io/v1/deepseek"


def test_url_helper_with_leading_slash():
    assert tessera.url("/openai") == "https://api.tesseraai.io/v1/openai"


def test_headers_requires_key():
    with pytest.raises(RuntimeError, match="Tessera key not set"):
        tessera.headers()


def test_headers_with_explicit_key():
    result = tessera.headers(key="tk_test123")
    assert result == {"X-Tessera-Key": "tk_test123"}


def test_headers_reads_env_var(monkeypatch):
    monkeypatch.setenv("TESSERA_KEY", "tk_env_key")
    # Without activate, headers() falls back to env
    result = tessera.headers()
    assert result["X-Tessera-Key"] == "tk_env_key"


def test_activate_requires_key():
    with pytest.raises(RuntimeError, match="Tessera key not provided"):
        tessera.activate()


def test_activate_reads_env_var(monkeypatch):
    monkeypatch.setenv("TESSERA_KEY", "tk_env_activate")
    status = tessera.activate()
    assert status.active is True
    assert tessera.is_active() is True


def test_activate_explicit_key():
    status = tessera.activate("tk_explicit")
    assert status.active is True
    assert tessera.headers() == {"X-Tessera-Key": "tk_explicit"}


def test_activate_feature_tag():
    tessera.activate("tk_test", feature_tag="checkout-summarizer")
    result = tessera.headers()
    assert result["X-Tessera-Key"] == "tk_test"
    assert result["X-Tessera-Feature-Tag"] == "checkout-summarizer"


def test_activate_custom_proxy_base():
    status = tessera.activate("tk_test", proxy_base="https://staging.tesseraai.io/v1")
    assert status.proxy_base == "https://staging.tesseraai.io/v1"
    assert tessera.url("openai") == "https://staging.tesseraai.io/v1/openai"


def test_deactivate_is_safe_when_inactive():
    # Should not raise.
    tessera.deactivate()
    assert tessera.is_active() is False


def test_activate_then_deactivate_lifecycle():
    tessera.activate("tk_test")
    assert tessera.is_active() is True
    tessera.deactivate()
    assert tessera.is_active() is False
    # headers() should now raise again
    with pytest.raises(RuntimeError):
        tessera.headers()


def test_re_activate_replaces_key():
    tessera.activate("tk_first")
    assert tessera.headers()["X-Tessera-Key"] == "tk_first"
    tessera.activate("tk_second")
    assert tessera.headers()["X-Tessera-Key"] == "tk_second"


def test_status_snapshot():
    tessera.activate("tk_test", feature_tag="alpha")
    s = tessera.status()
    assert s.active is True
    assert s.proxy_base == "https://api.tesseraai.io/v1"
    assert s.feature_tag == "alpha"
    # providers_patched may be empty in test env (no SDKs installed), or
    # contain anything that happened to import — just assert shape.
    assert isinstance(s.providers_patched, list)


def test_wrap_constructor_injects_base_url_and_headers(monkeypatch):
    """Drop a fake SDK module + class into sys.modules then verify the
    patcher wraps it correctly. Proves the wrap mechanic without needing the
    real openai package."""

    captured = {}

    class FakeClient:
        def __init__(self, api_key=None, base_url=None, default_headers=None, **kwargs):
            captured["api_key"] = api_key
            captured["base_url"] = base_url
            captured["default_headers"] = default_headers

    fake_module = types.SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    tessera.activate("tk_wrap_test")

    # Construct a FakeClient — wrap should inject base_url + Tessera key.
    instance = FakeClient(api_key="sk-user")  # noqa: F841 — side-effect captures
    assert captured["base_url"] == "https://api.tesseraai.io/v1/openai"
    assert captured["default_headers"] == {"X-Tessera-Key": "tk_wrap_test"}
    assert captured["api_key"] == "sk-user"


def test_wrap_does_not_override_explicit_base_url(monkeypatch):
    """If caller passes their own base_url, Tessera should NOT override it
    (caller-wins principle for transparent migration)."""

    captured = {}

    class FakeClient:
        def __init__(self, api_key=None, base_url=None, default_headers=None, **kwargs):
            captured["base_url"] = base_url
            captured["default_headers"] = default_headers

    fake_module = types.SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    tessera.activate("tk_wrap_test")

    FakeClient(api_key="sk-x", base_url="https://my-custom-proxy.example.com")
    assert captured["base_url"] == "https://my-custom-proxy.example.com"


def test_wrap_preserves_user_headers(monkeypatch):
    """Caller-provided default_headers should merge with Tessera's, not be
    overwritten. Tessera only adds X-Tessera-Key; caller-provided keys win
    on conflict (setdefault semantics)."""

    captured = {}

    class FakeClient:
        def __init__(self, api_key=None, base_url=None, default_headers=None, **kwargs):
            captured["default_headers"] = default_headers

    fake_module = types.SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    tessera.activate("tk_wrap_test")
    FakeClient(api_key="sk-x", default_headers={"X-User-Trace": "abc123"})

    headers = captured["default_headers"]
    assert headers["X-User-Trace"] == "abc123"  # user header preserved
    assert headers["X-Tessera-Key"] == "tk_wrap_test"  # Tessera injected


def test_deactivate_restores_original_constructor(monkeypatch):
    """After deactivate(), newly-created clients should NOT have Tessera
    patches applied. Verifies the restore callable works end-to-end."""

    captured = {}
    init_calls = []

    class FakeClient:
        def __init__(self, api_key=None, base_url=None, default_headers=None, **kwargs):
            init_calls.append("called")
            captured["base_url"] = base_url

    fake_module = types.SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    tessera.activate("tk_wrap_test")
    FakeClient(api_key="sk-x")
    assert captured["base_url"] == "https://api.tesseraai.io/v1/openai"

    tessera.deactivate()
    FakeClient(api_key="sk-x")  # should now use original __init__
    assert captured["base_url"] is None  # no Tessera injection
    assert len(init_calls) == 2
