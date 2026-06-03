---
name: testing
description: >
  Vitest testing patterns for Chrome MV3 extensions — Chrome API mocking,
  jsdom environment setup, IndexedDB polyfill, and coverage targets.
metadata:
  version: "1.0.0"
  reasoning_mode: tdd
---

# Testing Chrome Extensions with Vitest

## Environment

Chrome extensions run in a non-browser environment in tests. jsdom provides the DOM but has no `chrome.*` APIs. Every test touching Chrome APIs **must** mock them.

## Chrome API Mock Pattern

Create a shared mock in `src/test/setup.ts` (loaded via `vitest.config.ts` `setupFiles`).

> **CWS constraint:** Chrome Web Store rejects packages with underscore-prefixed directories (`__tests__`, `__mocks__`). Use `src/test/` for shared test setup and colocate tests as `*.test.ts` / `*.spec.ts` next to source files.

```typescript
import { vi } from 'vitest';

const mockChrome = {
  runtime: {
    onInstalled: { addListener: vi.fn() },
    onMessage: { addListener: vi.fn() },
    sendMessage: vi.fn(),
    getManifest: vi.fn(() => ({ version: '0.1.0', name: 'Extension' })),
  },
  storage: {
    local: {
      get: vi.fn().mockResolvedValue({}),
      set: vi.fn().mockResolvedValue(undefined),
      remove: vi.fn().mockResolvedValue(undefined),
    },
    sync: {
      get: vi.fn().mockResolvedValue({}),
      set: vi.fn().mockResolvedValue(undefined),
    },
  },
  tabs: {
    query: vi.fn().mockResolvedValue([]),
    create: vi.fn(),
  },
  action: {
    setIcon: vi.fn(),
    setBadgeText: vi.fn(),
  },
};

Object.assign(global, { chrome: mockChrome });
```

## IndexedDB

If your extension uses IndexedDB, add to test setup:
```typescript
import 'fake-indexeddb/auto';
```

## Test Structure

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('MyModule', () => {
  beforeEach(() => {
    vi.clearAllMocks();  // ALWAYS — prevents mock state leaking between tests
  });

  it('should handle normal case', () => {
    expect(myFunction('input')).toBe('expected');
  });

  it('should handle Chrome API call', async () => {
    vi.mocked(chrome.storage.local.get).mockResolvedValue({ key: 'value' });
    const result = await getFromStorage('key');
    expect(result).toBe('value');
    expect(chrome.storage.local.get).toHaveBeenCalledWith(['key']);
  });
});
```

## Test Location

Tests live as sibling `*.test.ts` files next to source — no `__tests__/` directories (CWS rejects underscore-prefixed dirs). Shared test setup lives in `src/test/`.

```
src/
  background/
    feature.ts
    feature.test.ts      ← co-located with source
  test/
    setup.ts             ← Chrome API mocks (vitest setupFiles)
```

## Coverage Targets

| Metric | Minimum |
|--------|---------|
| Lines | 70% |
| Branches | 60% |
| Functions | 70% |

## Commands

| Command | Speed | Use when |
|---------|-------|----------|
| `npm test` | ~15s | After every code change |
| `npx vitest run --coverage` | ~20s | Before committing or PR |
| `npx vitest watch` | — | During active development |

## Common Pitfalls

- Missing `vi.clearAllMocks()` in `beforeEach` → tests pollute each other
- Testing `chrome.*` calls without mocking → `TypeError: chrome is not defined`
- Forgetting `await` on `chrome.storage.*` calls (they return Promises)
- Testing implementation details instead of observable behavior
