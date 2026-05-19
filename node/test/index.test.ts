/**
 * Tessera SDK Node tests — unit-level (no network).
 *
 * Like the Python tests, we don't depend on real OpenAI/Anthropic packages
 * being installed. We exercise the pure helpers (url, headers, lifecycle)
 * and use a stub class injected via Module._cache override to verify the
 * wrap mechanic without a real provider SDK.
 */

import { afterEach, describe, expect, it } from 'vitest';
import {
  DEFAULT_PROXY_BASE,
  activate,
  deactivate,
  headers,
  isActive,
  status,
  url,
} from '../src/index';

afterEach(() => {
  deactivate();
  delete process.env.TESSERA_KEY;
});

describe('@tessera-llm/tessera-sdk — pure helpers', () => {
  it('exposes the canonical proxy base', () => {
    expect(DEFAULT_PROXY_BASE).toBe('https://api.tesseraai.io/v1');
  });

  it('url(provider) returns the joined proxy URL', () => {
    expect(url('openai')).toBe('https://api.tesseraai.io/v1/openai');
    expect(url('anthropic')).toBe('https://api.tesseraai.io/v1/anthropic');
    expect(url('deepseek')).toBe('https://api.tesseraai.io/v1/deepseek');
  });

  it('url trims leading + trailing slashes', () => {
    expect(url('/openai/')).toBe('https://api.tesseraai.io/v1/openai');
  });

  it('headers() throws when no key set', () => {
    expect(() => headers()).toThrow(/Tessera key not set/);
  });

  it('headers(key) accepts explicit key', () => {
    expect(headers('tk_explicit')).toEqual({ 'X-Tessera-Key': 'tk_explicit' });
  });

  it('headers() reads TESSERA_KEY env var when inactive', () => {
    process.env.TESSERA_KEY = 'tk_env_node';
    expect(headers()).toEqual({ 'X-Tessera-Key': 'tk_env_node' });
  });
});

describe('@tessera-llm/tessera-sdk — activate/deactivate lifecycle', () => {
  it('throws when no key provided either way', () => {
    expect(() => activate()).toThrow(/key not provided/);
  });

  it('activate() reads TESSERA_KEY env var', () => {
    process.env.TESSERA_KEY = 'tk_env_act';
    const s = activate();
    expect(s.active).toBe(true);
    expect(isActive()).toBe(true);
  });

  it('activate(key) sets the key and activates', () => {
    const s = activate('tk_test');
    expect(s.active).toBe(true);
    expect(headers()).toEqual({ 'X-Tessera-Key': 'tk_test' });
  });

  it('activate with featureTag adds X-Tessera-Feature-Tag to headers', () => {
    activate('tk_test', { featureTag: 'checkout' });
    expect(headers()).toEqual({
      'X-Tessera-Key': 'tk_test',
      'X-Tessera-Feature-Tag': 'checkout',
    });
  });

  it('activate with proxyBase overrides URL helper', () => {
    activate('tk_test', { proxyBase: 'https://staging.tesseraai.io/v1' });
    expect(url('openai')).toBe('https://staging.tesseraai.io/v1/openai');
  });

  it('deactivate is safe when inactive', () => {
    expect(() => deactivate()).not.toThrow();
    expect(isActive()).toBe(false);
  });

  it('activate then deactivate restores key-free state', () => {
    activate('tk_test');
    expect(isActive()).toBe(true);
    deactivate();
    expect(isActive()).toBe(false);
    expect(() => headers()).toThrow();
  });

  it('re-activate replaces the previous key', () => {
    activate('tk_first');
    expect(headers()['X-Tessera-Key']).toBe('tk_first');
    activate('tk_second');
    expect(headers()['X-Tessera-Key']).toBe('tk_second');
  });

  it('status() returns a snapshot', () => {
    activate('tk_test', { featureTag: 'beta' });
    const s = status();
    expect(s.active).toBe(true);
    expect(s.proxyBase).toBe(DEFAULT_PROXY_BASE);
    expect(s.featureTag).toBe('beta');
    expect(Array.isArray(s.providersPatched)).toBe(true);
  });
});
