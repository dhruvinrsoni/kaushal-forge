# project-templates

A base + overlay composition system for generating new projects with world-class scaffolding. Every new project starts with production-grade CI/CD, CLAUDE.md, skills, issue templates, security scanning, and conventions — from day one.

## Quick Start

```bash
# Generate a new project
node scripts/init-project.mjs --flavor react-vite-pwa --name my-dashboard --description "Admin dashboard"

# Preview what would be generated (no files written)
node scripts/init-project.mjs --flavor node-typescript --name my-lib --dry-run
```

## 8 Template Flavors

| Flavor | Stack | Best for |
|--------|-------|----------|
| `vanilla-pwa` | HTML/CSS/JS | Static PWAs, GitHub Pages apps |
| `node-typescript` | Node.js + TypeScript + Vitest | npm packages, CLI tools, libraries |
| `react-vite-pwa` | React + Vite + Tailwind | Web apps, dashboards, SPAs |
| `chrome-extension` | TypeScript + esbuild + Chrome MV3 | Browser extensions |
| `spring-boot` | Java 21 + Spring Boot 3 + Gradle | REST APIs, microservices |
| `scripts-toolbox` | Bash + PowerShell + Python | Script collections, toolboxes |
| `nano-app-collection` | Vanilla JS + Core framework | Micro-app dashboards |
| `python-tool` | Python 3.10+ + pytest + mypy + ruff | Python CLIs, utilities |

## What Every Generated Project Gets

### From the shared base layer:
- **CLAUDE.md** — AI-optimized project context with Critical File Map, commands, skills index
- **Security workflow** — secret detection + dependency audit (npm/pip/gradle-aware)
- **Label system** — Type + Priority + Status + Agent labels, auto-synced
- **Issue templates** — Structured bug reports and feature requests
- **PR template** — Checklist-driven pull request review
- **Repo-maintenance skill v2.0** — Adaptive cleanup with greedy optimization
- **.editorconfig** — Consistent formatting across editors
- **.gitattributes** — Cross-platform line ending normalization

### Plus flavor-specific:
- CI/CD workflows tuned for the stack
- Build configs, test setup, linting rules
- Copilot instructions and design philosophy docs
- Domain-specific skills (PWA, testing, nano-app protocol, etc.)

## Architecture

```
project-templates/
├── base/                  # Shared across ALL flavors
│   ├── CLAUDE.md.template
│   ├── .github/           # Labels, PR/issue templates, security workflow, skills
│   └── ...
├── flavors/               # One directory per flavor (only the delta from base)
│   ├── vanilla-pwa/
│   ├── node-typescript/
│   ├── react-vite-pwa/
│   ├── chrome-extension/
│   ├── spring-boot/
│   ├── scripts-toolbox/
│   ├── nano-app-collection/
│   └── python-tool/
├── scripts/
│   ├── init-project.mjs   # Generator (zero dependencies)
│   └── validate-templates.py
├── registry.yaml          # Template & skill registry
└── CLAUDE.md              # Meta-context for this repo
```

### How generation works:

1. **Copy** `base/` to target directory
2. **Overlay** `flavors/<flavor>/` on top (merges `.github/` directories)
3. **Replace** `{{TEMPLATE_VARS}}` in all `.template` files, strip suffix
4. **Append** `.overlay` file contents to matching base files
5. **Done** — project is ready for `git init`

## Generator Options

```
node scripts/init-project.mjs --flavor <flavor> --name <name> [options]

Required:
  --flavor       Template flavor (see table above)
  --name         Project name in kebab-case

Optional:
  --description  One-line project description (default: "A new project")
  --author       Author name (default: "Dhruvin Rupesh Soni")
  --github-user  GitHub username (default: "dhruvinrsoni")
  --license      MIT | Apache-2.0 (default: "MIT")
  --output       Output directory (default: ../<name>/)
  --dry-run      Preview without writing files
```

## Validation

```bash
python scripts/validate-templates.py
```

Checks: template variable consistency, SKILL.md frontmatter, required base files, flavor completeness.

## License

Apache License 2.0 — See [LICENSE](LICENSE)
