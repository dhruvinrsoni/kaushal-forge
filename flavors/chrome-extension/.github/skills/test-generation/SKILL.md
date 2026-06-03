---
name: test-generation
description: >
  Rules and patterns for generating test files for Chrome MV3 extensions.
  Covers coverage priority, mock patterns, and file generation workflow.
metadata:
  version: "1.0.0"
  reasoning_mode: tdd
---

# Test Generation for Chrome Extensions

## Coverage Priority Order

Write tests in this order for maximum impact per test written:

1. **Business logic in `src/background/`** — scorers, engines, data transformers
2. **Storage and state management** — database layer, settings
3. **Service layer** — API clients, circuit breakers
4. **Message handlers** — chrome.runtime.onMessage callbacks
5. **Popup logic** (lowest priority — harder to test, lower ROI)

## Workflow

```bash
# 1. Find what's uncovered
npx vitest run --coverage

# 2. Open coverage/lcov-report/index.html — find red lines
# 3. Generate tests for the uncovered file
# 4. Run tests to verify they pass
npm test
```

## File Generation Template

For a source file `src/background/feature.ts`, create `src/background/feature.test.ts` (co-located, no `__tests__/` directory — CWS rejects underscore-prefixed dirs):

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { exportedFunction } from '../feature.js';

// Mock Chrome APIs needed by this module
const mockChrome = { /* relevant subset */ };
Object.assign(global, { chrome: mockChrome });

describe('feature', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('exportedFunction', () => {
    it('handles normal input', () => { /* ... */ });
    it('handles empty/null input', () => { /* ... */ });
    it('handles error case', () => { /* ... */ });
  });
});
```

## Mock Granularity

- **Mock at the boundary** — mock `chrome.*`, `fetch()`, `IndexedDB` but not internal utilities
- **Do NOT mock** pure functions in `src/background/` — test them directly
- **Spy, don't replace** — use `vi.spyOn()` when you need the real implementation + just verify calls

## When Coverage Reveals Architectural Issues

If a function is very hard to test (requires 10+ mocks), it's probably doing too much. Consider:
- Extracting pure computation into a separate function (easy to test)
- Injecting Chrome API calls as dependencies rather than calling directly

## Auto-coverage Agent

See `.github/copilot/agents/test-coverage-agent.md` for the Copilot agent that automates test generation from coverage reports.
