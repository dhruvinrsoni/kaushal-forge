---
name: testing
description: >
  Vitest testing patterns — test structure, mocking, coverage targets,
  assertion patterns, and test file conventions.
metadata:
  version: "1.0.0"
  reasoning_mode: tdd
---

# Testing with Vitest

## Test Location Convention

```
src/
  module/
    feature.ts
    __tests__/
      feature.test.ts      # co-located with source
```

## Test Structure

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { myFunction } from '../feature.js';

describe('myFunction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle normal input', () => {
    expect(myFunction('input')).toBe('expected');
  });

  it('should handle edge case', () => {
    expect(myFunction('')).toBe('default');
  });

  it('should throw on invalid input', () => {
    expect(() => myFunction(null as any)).toThrow();
  });
});
```

## Mocking Patterns

### Module mock
```typescript
vi.mock('../dependency.js', () => ({
  fetchData: vi.fn().mockResolvedValue({ data: 'test' }),
}));
```

### Spy on existing method
```typescript
const spy = vi.spyOn(object, 'method').mockReturnValue('mocked');
// ... test ...
expect(spy).toHaveBeenCalledWith('arg');
```

### Timer mock
```typescript
vi.useFakeTimers();
// ... trigger timer-based code ...
vi.advanceTimersByTime(1000);
vi.useRealTimers();
```

## Coverage Targets

| Metric | Minimum | Ideal |
|--------|---------|-------|
| Lines | 70% | 90%+ |
| Branches | 60% | 80%+ |
| Functions | 70% | 90%+ |

## Commands

| Command | When |
|---------|------|
| `npm test` | Quick validation (run after every change) |
| `npm run test:watch` | During active development |
| `npm run test:coverage` | Before committing or for PR review |

## Common Pitfalls

- Forgetting `vi.clearAllMocks()` in `beforeEach` → tests leak state
- Testing implementation details instead of behavior
- Not testing error paths and edge cases
- Over-mocking — mock at boundaries, not internal utilities
