---
name: ui-components
description: >
  React component patterns for Vite+Tailwind PWAs — layer enforcement,
  error boundaries, dark mode, PWA-specific components, and anti-patterns.
metadata:
  version: "1.0.0"
  reasoning_mode: linear
---

# UI Components — React Vite PWA

## Layer Enforcement (Strict)

```
src/
├── components/    ← UI ONLY. No API calls. No business logic.
├── context/       ← State management. Coordinates API + UI.
├── hooks/         ← Custom React hooks. Can call utils.
├── utils/         ← Pure functions + API calls (only place for fetch/service calls)
├── types/         ← TypeScript definitions only
└── constants/     ← Config values, string literals
```

**Rule of thumb:** If it renders → `components/`. If it fetches → `utils/`. If it manages state → `context/`. If it's reusable logic → `hooks/`.

## Component Template

```typescript
// components/feature/FeatureName.tsx
import type { FC } from 'react';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const FeatureName: FC<Props> = ({ value, onChange }) => {
  return (
    <div className="...">
      {/* Render only — no fetch, no direct state mutation */}
    </div>
  );
};

export default FeatureName;
```

## Error Boundary

Wrap any async or third-party component:

```typescript
// components/common/ErrorBoundary.tsx
import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode; }
interface State { hasError: boolean; }

class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error: Error) { console.error('ErrorBoundary caught:', error); }
  render() {
    return this.state.hasError
      ? (this.props.fallback ?? <div>Something went wrong.</div>)
      : this.props.children;
  }
}
```

## Dark Mode with Tailwind

Uses `prefers-color-scheme` media query (Tailwind `darkMode: 'media'`):

```tsx
// Classes: default = light, dark: prefix = dark mode
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

To support manual toggle, switch `tailwind.config.js` to `darkMode: 'class'` and manage `document.documentElement.classList`.

## PWA Components

| Component | Purpose | Pattern |
|-----------|---------|---------|
| `OfflineIndicator` | Show banner when offline | `navigator.onLine` + `window.addEventListener('online'/'offline')` |
| `PWAInstallPrompt` | Custom install button | `window.addEventListener('beforeinstallprompt')` |
| `UpdateNotification` | "New version available" | `serviceWorker.waiting` state from `vite-plugin-pwa` |

## Anti-Patterns to Avoid

| Anti-pattern | Correct approach |
|-------------|-----------------|
| `fetch()` inside a component | Move to `utils/`, call via `context/` or `hook` |
| State in a component that's shared | Lift to `context/` |
| `any` type | Use proper interface or `unknown` |
| `useEffect` with no deps array | Almost always a bug — add deps |
| Direct localStorage in component | Abstract via `utils/storage.ts` |
