---
name: workflows-ci
description: >
  GitHub Actions CI/CD patterns for Chrome MV3 extensions — build, test,
  package, release, E2E, security scanning, and artifact management.
metadata:
  version: "2.0.0"
  reasoning_mode: linear
---

# CI/CD for Chrome Extensions

## Build Pipeline (`build.yml`)

Key principles:
- **Always use production build in CI** (`npm run build:prod`), not dev build
- **TypeScript check before build** (`npx tsc --noEmit`) — catches type errors esbuild misses
- **Lint with step summary** — JSON output for error/warning counts, human-readable for CI gate
- **Package the extension** every CI run — artifact proves it works end-to-end
- **Artifact naming** — reads `name` and `version` from `package.json` for consistent artifact filenames
- **Artifact retention** — 30 days is standard; reduce to 7 for storage savings

## E2E Pipeline (`e2e.yml`)

- Runs **Playwright** against a real Chromium browser with the extension loaded
- Extensions cannot run headless — CI uses `xvfb-run --auto-servernum`
- Path-filtered: only runs on PRs touching `src/**`, `e2e/**`, `playwright.config.ts`, `manifest.json`
- On failure: uploads `playwright-report/` and `test-results/` (traces) as artifacts

## Local Verification

Run the full CI pipeline locally before pushing:

```bash
npm run verify              # lint + build:dev + build:prod + unit tests + E2E
npm run verify -- --no-e2e  # skip E2E for faster feedback
npm run preflight           # verify + manifest checks + dist integrity + package zip
```

## Manifest Permission Audit

Run in `security.yml` to catch permission creep before shipping:

```bash
PERMS=$(node -e "const m = require('./manifest.json'); console.log(JSON.stringify(m.permissions || []))")
echo "Permissions: $PERMS"

echo "$PERMS" | grep -qE '"tabs"|"history"|"cookies"|"webRequest"' && \
  echo "::warning::Sensitive permission detected — verify it's necessary"
```

## Artifact Upload Pattern

```yaml
- name: Upload extension artifact
  uses: actions/upload-artifact@v4
  with:
    name: extension-${{ github.run_number }}
    path: ${{ env.ARTIFACT_NAME }}
    retention-days: 30
```

## Version Bumping in CI

**Never let CI bump versions automatically.** Versions are bumped via `scripts/release.mjs` locally. CI only validates that `package.json` and `manifest.json` are in sync:

```bash
PKG_VER=$(node -e "console.log(require('./package.json').version)")
MAN_VER=$(node -e "console.log(require('./manifest.json').version)")
[ "$PKG_VER" != "$MAN_VER" ] && echo "::error::Version mismatch: package=$PKG_VER, manifest=$MAN_VER" && exit 1
```

## Release Job Trigger

Release job only runs on version tags (`v*`):

```yaml
release:
  needs: build
  if: startsWith(github.ref, 'refs/tags/v')
```

Mark as prerelease for alpha/beta/rc tags:
```yaml
prerelease: ${{ contains(github.ref, '-alpha') || contains(github.ref, '-beta') || contains(github.ref, '-rc') }}
```

## When to Modify Workflows

| Change | Workflow to modify |
|--------|-------------------|
| Add new build step | `build.yml` -> build job |
| Add new permission to manifest | `security.yml` -> manifest audit section |
| Change test runner | `build.yml` -> test step |
| Change Node.js version | `build.yml` -> `node-version` field |
| Add/change E2E tests | `e2e.yml` -> e2e job |
| Add Docker support | Add `docker-build.yml` workflow |
