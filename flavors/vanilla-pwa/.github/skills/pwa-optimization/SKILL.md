---
name: pwa-optimization
description: >
  PWA best practices — service worker strategies, cache management, offline-first patterns,
  manifest optimization, Lighthouse audit targets.
metadata:
  version: "1.0.0"
  reasoning_mode: linear
---

# PWA Optimization

## Service Worker Strategies

| Strategy | When to use | Trade-off |
|----------|-------------|-----------|
| Cache-first | Static assets (CSS, JS, images) | Fast but may serve stale |
| Network-first | API calls, dynamic content | Fresh but slow offline |
| Stale-while-revalidate | Semi-static (fonts, config) | Fast + eventually fresh |

## Cache Versioning

Bump `CACHE_NAME` version when ANY cached asset changes. The service worker's `activate` event cleans old caches.

```javascript
const CACHE_NAME = 'app-v2'; // bump this
```

## Lighthouse PWA Checklist

Target: 100/100 on all categories.

- [ ] `manifest.json` has `name`, `short_name`, `icons` (192+512), `start_url`, `display`
- [ ] Service worker registered and functional
- [ ] All assets cached for offline use
- [ ] HTTPS enforced (GitHub Pages provides this)
- [ ] `<meta name="theme-color">` matches `manifest.json` theme_color
- [ ] `<meta name="viewport">` present
- [ ] Icons are maskable (safe zone test: https://maskable.app)
- [ ] Splash screen configured via manifest

## Offline Testing

1. DevTools → Application → Service Workers → check "Offline"
2. Navigate the app — all cached pages should load
3. Check console for fetch failures (missing cache entries)
4. Test: `python -m http.server 8000` then kill server → pages still load from cache

## Common Pitfalls

- Forgetting to add new files to the `ASSETS_TO_CACHE` array
- Cache name not bumped after asset changes → users see stale version
- `skipWaiting()` without `clients.claim()` → new SW installed but not controlling the page
- Missing `<link rel="manifest">` in HTML head
