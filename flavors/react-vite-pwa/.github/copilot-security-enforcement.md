# Security Enforcement Rules

## Absolute Prohibitions

| Rule | Severity |
|------|----------|
| No API keys in localStorage or source code | Critical |
| No `eval()` or `new Function()` with user input | Critical |
| No `dangerouslySetInnerHTML` without sanitization | Critical |
| No `http://` URLs in production (HTTPS only) | High |
| No `*` in CORS headers in production | High |

## Required Patterns

### API Key Storage
```typescript
// CORRECT: in-memory only, provided at runtime
const apiKey = sessionStorage.getItem('api-key'); // session-scoped

// WRONG: persisted in localStorage
localStorage.setItem('api-key', key); // survives browser restart
```

### Input Sanitization
```typescript
// CORRECT: sanitize before rendering user-generated content
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);

// WRONG: raw insertion
element.innerHTML = userInput;
```

### Content Security
```typescript
// CORRECT: use CSP headers
// <meta http-equiv="Content-Security-Policy" content="default-src 'self'">

// WRONG: no CSP, allowing arbitrary script injection
```

## Severity Levels

| Level | Action | Example |
|-------|--------|---------|
| Critical | Block commit, must fix | API key in source, eval with user input |
| High | Warn, fix before merge | HTTP URLs, missing sanitization |
| Medium | Note in review | Missing error boundary, no input validation |
| Low | Suggest improvement | Console.log in production code |
