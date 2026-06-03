# Design Philosophy — Future-Proof Enforcement Guide

## Layer Enforcement

```
src/
├── components/    # UI ONLY — no API calls, no business logic
├── context/       # State management — coordinates API + UI
├── hooks/         # Custom React hooks
├── utils/         # Pure functions, services (API calls only here)
├── types/         # TypeScript definitions
└── constants/     # Config values, literals
```

**Rule:** Components render. Context coordinates. Utils compute. Types define. Constants configure.

## Patterns to Follow

### 1. Standardized Interfaces
```typescript
// GOOD: interface for all external service calls
interface ServiceResponse<T> {
  data: T;
  error?: string;
  status: 'success' | 'error' | 'loading';
}

// BAD: ad-hoc response shapes per service
```

### 2. Defensive Error Handling
```typescript
// GOOD: Error boundary + graceful degradation
<ErrorBoundary fallback={<ErrorFallback />}>
  <RiskyComponent />
</ErrorBoundary>

// BAD: unhandled promise rejections, uncaught renders
```

### 3. Versioned Data Structures
```typescript
// GOOD: version field for localStorage data
interface StoredData {
  version: 2;
  chats: Chat[];
}

// BAD: raw unversioned data that breaks on schema changes
```

### 4. Extension Points
```typescript
// GOOD: provider pattern for swappable implementations
interface LLMProvider {
  chat(messages: Message[]): Promise<string>;
  models(): Promise<string[]>;
}

// BAD: hardcoded to a single API
```

## Anti-Patterns to Flag

- Direct API calls in components (should be in `utils/`)
- Business logic in event handlers (should be in `context/` or `hooks/`)
- `any` type without justification
- Hardcoded strings that should be constants
- Missing error boundaries around async UI
- localStorage without version migration logic
