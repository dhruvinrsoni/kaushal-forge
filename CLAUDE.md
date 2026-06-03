# CLAUDE.md — kaushal-forge Project Context

Project-specific instructions for Claude Code. Loaded automatically when working in this repo.

---

## Project

Repeatable, model-agnostic **career-toolkit generator**: from one person's raw history it produces a
LinkedIn rewrite, multi-variant LaTeX résumés (compiled to PDF, 1- and 2-page), matching cover letters,
and a strategy pack — reproducibly, **on any model** (Opus → Haiku).

**Stack:** Python 3.10+ (deterministic engine) · LaTeX / Tectonic · Claude Code skill + portable prompts

🔒 **Proprietary / All-Rights-Reserved. Private repo.** Personal data, generated output, and PDFs are
never committed (see `.gitignore`).

---

## Why it runs on cheap models

Work is split so the model never has to be clever:

- **Mechanical** (render LaTeX, compile PDFs, count characters, scan for leaks, check page counts) →
  deterministic Python in `engine/`. Zero intelligence required; identical on any machine.
- **Judgement** (write tailored content) → the AI, but **confined to filling rigid JSON schemas** with a
  worked example beside each (`skill/kaushal-forge/` or `prompts/`). A weak model pattern-matches instead
  of inventing.
- **`engine/verify.py` is a hard gate** — exits non-zero on any leak, stray HTML entity, char-limit, or
  page-count failure.

---

## Critical File Map

Navigate here first — don't broad-search when the location is known:

| What | Where |
|------|-------|
| Engine (mechanical) | `engine/` — `bootstrap.py`, `intake_dump.py`, `render_{resumes,coverletters,linkedin,strategy}.py`, `build_pdfs.py`, `verify.py` |
| LaTeX styles | `engine/templates/styles/cf-{ats,modern,twocol,letter}.tex` |
| Claude skill (judgement) | `skill/kaushal-forge/` — `SKILL.md`, `phases/P1–P6`, `schemas/`, `rules/`, `examples/` (anonymized gold) |
| Portable prompt pack | `prompts/` — `00-how-to-use.md`, `P1`–`P6` (for non-Claude models) |
| Config | `config.example.yaml` → copy to `config.yaml` (gitignored) |
| Pipeline I/O | `inbox/` (raw) → `work/` (JSON + strategy) → `output/` (PDFs + md) — contents gitignored |
| CI fixtures | `tests/fixtures/` — fully fictional sample run for the render-smoke |

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `python engine/bootstrap.py` | install deps + LaTeX engine (Tectonic) |
| `python engine/render_resumes.py` | `work/{profile,variants}.json` → `output/Resumes/` |
| `python engine/render_coverletters.py` | `work/letters.json` → `output/CoverLetters/` |
| `python engine/render_linkedin.py` | `work/linkedin.json` → `output/LinkedIn/` |
| `python engine/render_strategy.py` | `work/strategy/*.md` → `output/Strategy/` |
| `python engine/build_pdfs.py` | compile every `.tex` with Tectonic |
| `python engine/verify.py` | the gate: leaks, entities, char limits, page counts |

Pipeline order: intake → P1 `profile.json` → P2 `targeting.json` → P3 `linkedin.json` →
P4 `variants.json` → P5 `letters.json` → P6 `strategy/*.md`; each AI phase is paired with a render script.

---

## Domain Skills (On-Demand Context)

Load `.github/skills/<name>/SKILL.md` for deep domain knowledge:

| Skill | Load when... |
|-------|-------------|
| `kaushal-forge` | Running or maintaining the generator pipeline (orchestrator `SKILL.md` + phases P1–P6) |
| `repo-maintenance` | Cleanup, dead-code audit, file reorganization |
| `systematic-debugging` | Tracking down a failing render or verify |
| `testing` | Adding or adjusting CI fixtures / smoke checks |

> To use the `kaushal-forge` skill in Claude Code, symlink or copy `skill/kaushal-forge/` into
> `~/.claude/skills/` (or a project-level `.claude/skills/`).

---

## Key Conventions

- **Commit convention** — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, `license:` prefixes
- **Never commit** `config.yaml`, `work/*`, `output/*`, `*.pdf`, personal data, or the Tectonic binary (all gitignored)
- **Examples stay fictional** — `skill/kaushal-forge/examples/` and `tests/fixtures/` use the
  "Asha Verma / Acme Cloud" persona; never real career data
- **Engine stays deterministic and path-relative** — it derives paths from its own location, so the repo can move without breaking it

---

## Architecture notes

- The engine needs no intelligence: keep it deterministic. All judgement lives in the schemas + examples the model fills.
- Not a PyPI package — KaushalForge runs as scripts; there is intentionally **no publish workflow**.
- `tests/fixtures/` drives the CI **render-smoke** (`.github/workflows/ci.yml`): render → `build_pdfs.py` → `verify.py`.
