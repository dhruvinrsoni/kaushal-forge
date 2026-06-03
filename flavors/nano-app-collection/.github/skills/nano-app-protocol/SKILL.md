---
name: nano-app-protocol
description: >
  Protocol for creating and modifying nano-apps. Covers required HTML elements,
  Core framework integration, state management, and dashboard registration.
metadata:
  version: "1.0.0"
  reasoning_mode: linear
---

# Nano-App Protocol

## Creating a New Nano-App

### 1. Create the directory
```
my-app/
  index.html
  app.js
  style.css (optional — inline styles OK for simple apps)
```

### 2. Required HTML elements
```html
<!-- Navigation back to dashboard -->
<a href="../">&larr; Back to Dashboard</a>

<!-- Metadata display (optional but recommended) -->
<span id="meta-created">—</span>
<span id="meta-updated">—</span>

<!-- Required scripts (in this order) -->
<script src="../app_registry.js"></script>
<script src="../core.js"></script>
<script src="app.js"></script>
```

### 3. Initialize with Core
```javascript
const { instanceId, State, renderMeta } = Core.init('my-app');
```

### 4. State management
```javascript
// Save (auto-namespaced by instanceId)
State.save('key', value);

// Load with fallback
const value = State.load('key', defaultValue);

// Clear all state for this instance
State.clear();
```

### 5. Register in dashboard
Add entry to `app_registry.js`:
```javascript
{
  id: 'my-app',
  name: 'My App',
  shortCode: 'MA',
  description: 'What it does in one line.',
  path: 'my-app/',
  tags: ['category'],
  version: '0.1.0',
}
```

## Rules

- Every app is a **self-contained directory** — understandable by reading it alone
- All state via `State.save/load` — never raw `localStorage`
- Works on `file://` — no `fetch()`, no CORS, use script-injection pattern
- Per-tab instance isolation via `sessionStorage` + `?instanceId=` URL param
- No external dependencies — zero CDN links, zero npm packages
