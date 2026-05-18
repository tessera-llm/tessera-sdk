/**
 * Tessera Optimize Layer — drop-in cost optimization for LLM SDKs.
 *
 * One line of code patches OpenAI / Anthropic / Mistral / Groq / Cohere
 * client constructors so requests route through Tessera's measurement +
 * auto-optimize proxy. Your existing application code runs unchanged.
 *
 * Typical use:
 *
 *   import { activate } from "@tessera-llm/sdk";
 *   activate("tk_your_tessera_key");
 *
 * After `activate()`, any subsequent `new OpenAI()` / `new Anthropic()` /
 * other supported SDK client created in this Node process transparently
 * forwards requests through `api.tesseraai.io`. Your existing provider
 * keys (`sk-...`, `sk-ant-...`) flow upstream untouched.
 *
 * For providers without an official Node SDK (DeepSeek/Together/Fireworks/
 * OpenRouter/Perplexity/Cerebras/xAI), use `url(provider)` + `headers()`
 * to wire an `OpenAI` client manually.
 *
 * Locked 2026-05-17 — γ-mode integration per founder direction
 * ("Cloudflare-стиль: дай ключ, остальное мы делаем").
 */

export const DEFAULT_PROXY_BASE = 'https://api.tesseraai.io/v1';

export interface ProxyStatus {
  active: boolean;
  providersPatched: string[];
  proxyBase: string;
  featureTag: string | null;
}

export interface ActivateOptions {
  /** Override the proxy origin. Default https://api.tesseraai.io/v1. */
  proxyBase?: string;
  /**
   * Attach a default `X-Tessera-Feature-Tag` header to every patched request
   * — useful for per-workload attribution when one app has multiple LLM
   * features (e.g. "checkout-summarizer", "support-replies").
   */
  featureTag?: string;
}

type Restore = () => void;

interface InternalState {
  active: boolean;
  key: string | null;
  proxyBase: string;
  featureTag: string | null;
  patched: Array<{ provider: string; restore: Restore }>;
}

const state: InternalState = {
  active: false,
  key: null,
  proxyBase: DEFAULT_PROXY_BASE,
  featureTag: null,
  patched: [],
};

/** Tessera proxy URL for a given provider. */
export function url(provider: string): string {
  const base = state.proxyBase.replace(/\/+$/, '');
  const clean = provider.replace(/^\/+/, '').replace(/\/+$/, '');
  return `${base}/${clean}`;
}

/** Headers required to authenticate against Tessera. */
export function headers(key?: string): Record<string, string> {
  const resolved = key ?? state.key ?? process.env.TESSERA_KEY;
  if (!resolved) {
    throw new Error(
      'Tessera key not set. Call activate("tk_...") first or pass key to headers().',
    );
  }
  const result: Record<string, string> = { 'X-Tessera-Key': resolved };
  if (state.featureTag) {
    result['X-Tessera-Feature-Tag'] = state.featureTag;
  }
  return result;
}

/** True if activate() has been called and patches are installed. */
export function isActive(): boolean {
  return state.active;
}

/** Snapshot the current SDK state — useful in health checks + logging. */
export function status(): ProxyStatus {
  return {
    active: state.active,
    providersPatched: state.patched.map((p) => p.provider),
    proxyBase: state.proxyBase,
    featureTag: state.featureTag,
  };
}

/**
 * Install Tessera patches globally.
 *
 * @param key Tessera API key (`tk_...`). Falls back to `process.env.TESSERA_KEY` if omitted.
 * @param options Override proxy base or attach a default feature tag.
 * @returns Current proxy status.
 * @throws If neither argument nor env var provides a key.
 */
export function activate(key?: string, options: ActivateOptions = {}): ProxyStatus {
  const resolved = key ?? process.env.TESSERA_KEY;
  if (!resolved) {
    throw new Error(
      'Tessera key not provided. Pass key to activate() or set TESSERA_KEY env var.',
    );
  }

  if (state.active) {
    // Re-activating with new args: deactivate first so we can re-patch
    // with the new state cleanly.
    deactivate();
  }

  state.key = resolved;
  state.proxyBase = (options.proxyBase ?? DEFAULT_PROXY_BASE).replace(/\/+$/, '');
  state.featureTag = options.featureTag ?? null;
  state.active = true;
  state.patched = [];

  for (const patcher of PATCHERS) {
    try {
      const restore = patcher();
      if (restore) {
        state.patched.push({ provider: patcher.providerName, restore });
      }
    } catch (err) {
      // Best-effort patching — log and skip on per-SDK failures.
      // eslint-disable-next-line no-console
      console.warn(`tessera: failed to patch ${patcher.providerName}:`, err);
    }
  }

  return status();
}

/** Reverse all patches installed by activate(). Safe to call when inactive. */
export function deactivate(): void {
  for (const { restore } of [...state.patched].reverse()) {
    try {
      restore();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn('tessera: failed to restore patch:', err);
    }
  }
  state.active = false;
  state.patched = [];
  state.key = null;
  state.featureTag = null;
}

// ─── per-provider patchers ──────────────────────────────────────────────────

type PatcherFn = (() => Restore | null) & { providerName: string };

function safeRequire(moduleName: string): unknown {
  try {
    // Use Function-constructed eval require to avoid bundler resolution of
    // optional peer deps. We're explicitly tolerating "not installed".
    // eslint-disable-next-line @typescript-eslint/no-implied-eval
    const req = new Function('m', 'return require(m)') as (m: string) => unknown;
    return req(moduleName);
  } catch {
    return null;
  }
}

interface PatchedClass {
  // Constructor signature we wrap. Caller's args are forwarded with our
  // baseURL + headers injected when missing.
  new (...args: unknown[]): unknown;
}

/**
 * Wrap a class so newly-constructed instances pass through Tessera.
 *
 * Most modern LLM SDKs (OpenAI, Anthropic) take a single options object:
 * `new OpenAI({ apiKey, baseURL, defaultHeaders, ... })`. We mutate that
 * options object to inject baseURL + Tessera key when absent (caller wins).
 */
function wrapClass(
  hostModule: Record<string, unknown>,
  className: string,
  options: {
    baseUrlField?: string;
    headersField?: string;
    proxyPath: string;
  },
): Restore | null {
  const original = hostModule[className] as PatchedClass | undefined;
  if (typeof original !== 'function') return null;

  const baseUrlField = options.baseUrlField ?? 'baseURL';
  const headersField = options.headersField ?? 'defaultHeaders';
  const proxyUrl = url(options.proxyPath);

  class Patched extends (original as unknown as { new (...args: unknown[]): object }) {
    constructor(...args: unknown[]) {
      const first = args[0] as Record<string, unknown> | undefined;
      const opts: Record<string, unknown> = first && typeof first === 'object' ? { ...first } : {};
      if (!(baseUrlField in opts) || opts[baseUrlField] === undefined) {
        opts[baseUrlField] = proxyUrl;
      }
      const existingHeaders = (opts[headersField] as Record<string, string> | undefined) ?? {};
      const merged: Record<string, string> = { ...existingHeaders };
      for (const [k, v] of Object.entries(headers())) {
        if (!(k in merged)) merged[k] = v;
      }
      opts[headersField] = merged;
      args[0] = opts;
      // eslint-disable-next-line constructor-super
      super(...args);
    }
  }

  // Preserve static members + prototype chain attributes the wrapped class
  // may have. `extends` already covers prototype + .name; copy own statics.
  Object.assign(Patched, original);
  Object.defineProperty(Patched, 'name', { value: className });

  hostModule[className] = Patched;

  return () => {
    hostModule[className] = original;
  };
}

function makePatcher(
  providerName: string,
  fn: () => Restore | null,
): PatcherFn {
  const wrapper = (() => fn()) as PatcherFn;
  wrapper.providerName = providerName;
  return wrapper;
}

const patchOpenAI = makePatcher('openai', () => {
  const mod = safeRequire('openai') as Record<string, unknown> | null;
  if (!mod) return null;
  const restorers: Restore[] = [];
  for (const cls of ['OpenAI', 'default']) {
    const r = wrapClass(mod, cls, { proxyPath: 'openai' });
    if (r) restorers.push(r);
  }
  return restorers.length > 0 ? () => restorers.forEach((r) => r()) : null;
});

const patchAnthropic = makePatcher('anthropic', () => {
  const mod = safeRequire('@anthropic-ai/sdk') as Record<string, unknown> | null;
  if (!mod) return null;
  const restorers: Restore[] = [];
  for (const cls of ['Anthropic', 'default']) {
    const r = wrapClass(mod, cls, { proxyPath: 'anthropic' });
    if (r) restorers.push(r);
  }
  return restorers.length > 0 ? () => restorers.forEach((r) => r()) : null;
});

const patchMistral = makePatcher('mistral', () => {
  const mod = safeRequire('@mistralai/mistralai') as Record<string, unknown> | null;
  if (!mod) return null;
  const restorers: Restore[] = [];
  for (const cls of ['Mistral', 'default']) {
    const r = wrapClass(mod, cls, {
      baseUrlField: 'serverURL',
      proxyPath: 'mistral',
    });
    if (r) restorers.push(r);
  }
  return restorers.length > 0 ? () => restorers.forEach((r) => r()) : null;
});

const patchGroq = makePatcher('groq', () => {
  const mod = safeRequire('groq-sdk') as Record<string, unknown> | null;
  if (!mod) return null;
  const restorers: Restore[] = [];
  for (const cls of ['Groq', 'default']) {
    const r = wrapClass(mod, cls, { proxyPath: 'groq' });
    if (r) restorers.push(r);
  }
  return restorers.length > 0 ? () => restorers.forEach((r) => r()) : null;
});

const patchCohere = makePatcher('cohere', () => {
  const mod = safeRequire('cohere-ai') as Record<string, unknown> | null;
  if (!mod) return null;
  const restorers: Restore[] = [];
  for (const cls of ['CohereClient', 'CohereClientV2', 'default']) {
    const r = wrapClass(mod, cls, { proxyPath: 'cohere' });
    if (r) restorers.push(r);
  }
  return restorers.length > 0 ? () => restorers.forEach((r) => r()) : null;
});

const PATCHERS: PatcherFn[] = [
  patchOpenAI,
  patchAnthropic,
  patchMistral,
  patchGroq,
  patchCohere,
];
