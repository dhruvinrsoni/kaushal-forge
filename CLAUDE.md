# CLAUDE.md — project-templates

Meta-template repository for generating new projects with best-practice scaffolding.

---

## Project

A base + overlay composition system with 8 template flavors. A generator script (`scripts/init-project.mjs`) merges `base/` + `flavors/<name>/` into a new project directory with variable substitution.

**Stack:** Node.js (generator) · Python (validator) · Zero external dependencies

---

## Critical File Map

| What | Where |
|------|-------|
| Generator script | `scripts/init-project.mjs` |
| Validator script | `scripts/validate-templates.py` |
| Shared base layer | `base/` |
| All 8 flavors | `flavors/<name>/` |
| Template registry | `registry.yaml` |
| Base CLAUDE.md skeleton | `base/CLAUDE.md.template` |
| Repo-maintenance skill v2.0 | `base/.github/skills/repo-maintenance/SKILL.md` |

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `node scripts/init-project.mjs --flavor <f> --name <n>` | Generate a new project |
| `node scripts/init-project.mjs --flavor <f> --name <n> --dry-run` | Preview generation |
| `python scripts/validate-templates.py` | Validate all templates |

---

## Architecture

```
base/           → shared files (all flavors get this)
flavors/<name>/ → flavor-specific delta (overwrites/extends base)
*.template      → files with {{VARS}} that get replaced during generation
*.overlay       → content appended to matching base file (e.g., CLAUDE.md.overlay → CLAUDE.md)
```

### Adding a New Flavor

1. Create `flavors/<name>/` directory
2. Add flavor-specific files (only the delta from base)
3. Add `CLAUDE.md.overlay` for flavor-specific CLAUDE.md sections
4. Add `<name>` to `FLAVORS` array in `scripts/init-project.mjs`
5. Add entry to `registry.yaml`
6. Run `python scripts/validate-templates.py` to verify

---

## Key Conventions

- `{{TEMPLATE_VARS}}` — uppercase, double-braces, underscores
- `.template` suffix → stripped during generation, vars replaced
- `.overlay` suffix → appended to matching base file, then removed
- Skills follow agentskills-garden spec (YAML frontmatter with name + description)
