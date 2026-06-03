---
name: maintenance
description: >
  Chrome extension maintenance workflows — bug fixes, releases, version
  management, and Chrome Web Store submission process.
metadata:
  version: "2.0.0"
  reasoning_mode: linear
---

# Chrome Extension Maintenance

## Bug Fix Workflow

```
1. Reproduce bug manually (install unpacked extension -> trigger bug)
2. Write a failing test that captures the behavior
3. Fix the root cause in src/
4. npm run verify -- --no-e2e
5. Test the fix manually in Chrome
6. git commit -m "fix: <description>"
7. If shipping: node scripts/release.mjs patch
```

## New Feature Workflow

```
1. Load relevant domain skill -> plan implementation
2. Implement in src/
3. Write tests for new logic (colocated *.test.ts, no __tests__/ dirs)
4. npm run verify
5. Manual test in Chrome (load unpacked from dist/)
6. git commit -m "feat: <description>"
7. If shipping: node scripts/release.mjs minor
```

## Release Workflow

```bash
node scripts/release.mjs <patch|minor|major>
# Validates -> bumps version -> syncs manifest -> builds -> packages -> tags -> pushes -> GitHub Release
```

### Pre-release verification

```bash
npm run preflight   # Full verify + manifest checks + dist integrity + package zip + git status
```

### Version strategy
- `patch` — bug fixes, no new permissions
- `minor` — new features, backward compatible
- `major` — breaking changes or new permissions (requires user re-consent)

## Version Sync Rule

**Always bump version in `package.json` first**, then run `npm run sync-version` (or let `release.mjs` do it).

Never manually edit `manifest.json` version — it's always derived from `package.json`.

## Chrome Web Store Submission Checklist

- [ ] `npm run preflight` passed
- [ ] `npm run package` succeeded -> versioned zip in `release/`
- [ ] Version in `manifest.json` is higher than current store version
- [ ] Permissions haven't changed (if added: justify in update notes)
- [ ] Privacy policy URL valid (if extension accesses user data)
- [ ] Tested in Chrome on all supported platforms (Windows, macOS, Linux)
- [ ] Screenshots updated if UI changed
- [ ] Store description updated if features changed

## CWS Naming Constraints

Chrome Web Store rejects packages with underscore-prefixed directories. Never use `__tests__/`, `__mocks__/`, or `__fixtures__/` in `dist/`. The `package.mjs` script automatically excludes underscore-prefixed entries from the zip.

## Loading Unpacked for Testing

1. Go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `dist/` directory (after `npm run build:dev`)

## Debugging Service Worker

1. Go to `chrome://extensions/`
2. Find your extension -> click "Service worker" link
3. DevTools opens for the background service worker
4. Check Console for errors, use Sources for breakpoints
