# Onboarding — get productive in ~15 minutes

**Who/what:** A new operator (you want to *run* KaushalForge for a real person) or a contributor (you want to *change the engine*). This page gets you to a green pipeline locally without ever touching a real `config.yaml`, `work/`, or `output/`, then maps the real loop and where everything lives.

> 🔒 Proprietary & private — All-Rights-Reserved (see [LICENSE](../LICENSE)). Every example below uses the fictional CI persona **Asha Verma / Acme Cloud** baked into [tests/fixtures/](../tests/fixtures). Real personal data, generated PDFs, and your `config.yaml`/`inbox/`/`work/`/`output/` are gitignored and never committed.

---

## Prerequisites

- **Python 3.10+** and **git**. CI pins **3.12** ([.github/workflows/ci.yml](../.github/workflows/ci.yml)); the devcontainer uses the `python:3.12` image. Anything 3.10+ runs the engine.
- **Tectonic** (the LaTeX engine) is **auto-installed** — you do not pre-install a TeX distribution. [engine/bootstrap.py](../engine/bootstrap.py) downloads the right release asset for your OS into `engine/.bin/` and records the path in `engine/.tectonic_path`. If the download fails it warns and you can still compile every `build-*.tex` on Overleaf.
- Python deps are just **`pyyaml`** and **`pypdf`** (plus **`ruff`** for linting). No virtualenv is required, but one is fine.
- Optional: **VS Code + Dev Containers** — open the repo in the container ([.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json)) and `postCreateCommand` runs `pip install pyyaml pypdf ruff` for you.

---

## First 5 minutes — SEE IT WORK (isolated scratch dir)

This reproduces exactly what the `render-smoke` job in CI does, but in a throwaway directory so you **never touch your real `config.yaml`, `work/`, or `output/`**.

**Why a scratch dir works:** every engine script resolves its root as the *parent of the `engine/` folder it lives in* — e.g. `HERE = .../engine`, `ROOT = os.path.dirname(HERE)` ([engine/build_pdfs.py:5](../engine/build_pdfs.py), [engine/verify.py:7](../engine/verify.py)). It then reads `ROOT/config.yaml`, `ROOT/work/*.json`, and writes `ROOT/output/`. So if you copy `engine/` into a temp dir and place `config.yaml` + `work/` beside it, **that temp dir becomes ROOT** and nothing in your real checkout is read or written.

Run these from the repo root (`bash`; on Windows use Git Bash or the devcontainer):

```bash
# 1. make a throwaway scratch dir and copy the engine + the fictional fixtures into it
REPO="$PWD"
SCRATCH="$(mktemp -d)"
cp -r "$REPO/engine" "$SCRATCH/engine"
cp "$REPO/tests/fixtures/config.yaml" "$SCRATCH/config.yaml"   # Asha Verma / Acme Cloud
mkdir -p "$SCRATCH/work"
cp "$REPO/tests/fixtures"/*.json "$SCRATCH/work/"              # profile / targeting / variants / linkedin / letters
cp -r "$REPO/tests/fixtures/strategy" "$SCRATCH/work/strategy" # the P6 markdown
cd "$SCRATCH"

# 2. install Tectonic + python deps INTO the scratch engine (writes engine/.tectonic_path)
python engine/bootstrap.py

# 3. render the four feeds -> output/{Resumes,CoverLetters,LinkedIn,Strategy}
python engine/render_resumes.py
python engine/render_coverletters.py
python engine/render_linkedin.py
python engine/render_strategy.py

# 4. compile every .tex and verify
python engine/build_pdfs.py    # prints a file / exit / pages table; ends "TOTAL=17  FAIL=0"
python engine/verify.py        # the gate -> "VERIFY OK ..."
```

**What to expect.** The fixture has 2 role variants (`01-software-engineer-backend`, `03-ai-genai-engineer`). `render_resumes.py` writes one **Master** folder (`09-master-2page`) plus, for each variant, a 1-page and a 2-page folder (`two_page: "all"` in the fixture config) — 5 folders, each with `build-ats.tex`, `build-modern.tex`, `build-twocol.tex`. That's **15 résumé PDFs + 2 cover-letter PDFs = 17 PDFs**, so `build_pdfs.py` prints **`TOTAL=17  FAIL=0`** and `verify.py` prints **`VERIFY OK — no leaks, no stray entities, char limits respected, page counts correct.`**

`verify.py` is a hard gate that checks four things ([engine/verify.py:21-57](../engine/verify.py)): forbidden-term leaks, stray HTML entities (`&gt;` etc.), LinkedIn char limits (headline ≤220, about ≤2600), and PDF page counts (role 1-pagers = 1 page; `*-2page` and `09-master` = 2; letters = 1).

```bash
# 5. throw the scratch dir away when you're done
cd "$REPO" && rm -rf "$SCRATCH"
```

> If `build_pdfs.py` prints `ERROR: Tectonic not found`, re-run `python engine/bootstrap.py` (or compile on Overleaf). It looks for Tectonic via `$CAREERFORGE_TECTONIC`, then `engine/.tectonic_path`, then `PATH`, then `engine/.bin/` ([engine/build_pdfs.py:8-19](../engine/build_pdfs.py)).

---

## The real loop, in one screen

For an actual person you work in the **repo root** (no scratch dir). `inbox/`, `work/`, `output/`, and `config.yaml` are gitignored — clear them (keep each `.gitkeep`) to start a fresh person.

```text
bootstrap.py            once: deps + Tectonic
   │
cp config.example.yaml config.yaml      fill person / contact / targets / verify.forbidden_terms
   │
inbox/                  drop raw data (LinkedIn "Get a copy of your data" export, reviews, old resume, GitHub text)
   │
intake_dump.py          -> work/00-raw-dump.txt
   │
P1..P6  (the AI)        each phase fills ONE rigid schema -> work/*.json | work/strategy/*.md
   │  P1 profile.json · P2 targeting.json · P3 linkedin.json · P4 variants.json · P5 letters.json · P6 strategy/*.md
   │
render_{resumes,coverletters,linkedin,strategy}.py    work/*.json -> output/*
   │
build_pdfs.py           compile every .tex with Tectonic (prints page table)
   │
verify.py               GATE — must print "VERIFY OK"
```

The AI phases are the only non-deterministic step, and they are confined to **emitting valid JSON / templated markdown** — never raw LaTeX, never prose outside the schema (the scripts do all rendering and escaping). See [RUNBOOK.md](../RUNBOOK.md) for the phase-by-phase table (which file each phase reads and produces) and the refresh-later loop, and [05-ai-layer.md](05-ai-layer.md) for how the phases and schemas are structured.

---

## Loading the skill in Claude Code

The AI phases are orchestrated by the **`kaushal-forge`** skill at [.github/skills/kaushal-forge/](../.github/skills/kaushal-forge). To make Claude Code discover it, symlink or copy that directory into your skills folder:

```bash
# user-level (works in any directory)
ln -s "$PWD/.github/skills/kaushal-forge" ~/.claude/skills/kaushal-forge
# or copy it instead of symlinking
cp -r .github/skills/kaushal-forge ~/.claude/skills/kaushal-forge
# or project-level
mkdir -p .claude/skills && ln -s "$PWD/.github/skills/kaushal-forge" .claude/skills/kaushal-forge
```

Then invoke the **`kaushal-forge`** skill; it walks P1→P6, reading each phase prompt (schema + rules + a gold example inline) from `.github/skills/kaushal-forge/phases/PN-*.md`. On a non-Claude model, use the portable copy-paste pack in `prompts/` instead (start with `prompts/00-how-to-use.md`).

---

## Where everything lives

| Path | What |
|---|---|
| [README.md](../README.md) · [RUNBOOK.md](../RUNBOOK.md) · [MASTER-PLAN.md](../MASTER-PLAN.md) | quickstart · operator steps · full design/rationale |
| [engine/](../engine) | the deterministic Python: `bootstrap.py`, `intake_dump.py`, `render_*.py`, `build_pdfs.py`, `verify.py` |
| `engine/templates/styles/` | the LaTeX styles (`cf-ats`, `cf-modern`, `cf-twocol`, `cf-letter`) injected with your accent |
| [.github/skills/kaushal-forge/](../.github/skills/kaushal-forge) | the AI orchestrator skill: `SKILL.md`, `phases/`, `rules/`, `schemas/`, `examples/` |
| `prompts/` | copy-paste prompt pack for non-Claude models |
| [tests/fixtures/](../tests/fixtures) | the fully-fictional Asha Verma sample run the CI smoke exercises |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | CI: JSON validation + the render→build→verify gate |
| [Makefile](../Makefile) · `pyproject.toml` · [config.example.yaml](../config.example.yaml) | shortcuts · Python tooling · config template |
| `config.yaml` · `inbox/` · `work/` · `output/` | runtime I/O — **gitignored**, never committed |

---

## Makefile shortcuts & the devcontainer

Run from the repo root once you have a staged `config.yaml` + `work/`:

| Command | Does |
|---|---|
| `make dev` | `pip install pyyaml pypdf ruff` |
| `make lint` / `make format` | `ruff check engine` / `ruff format engine` |
| `make compile` | `python -m py_compile engine/*.py` (fast sanity check; same step CI runs) |
| `make smoke` | full pipeline: all four `render_*.py` → `build_pdfs.py` → `verify.py` |
| `make verify` | just the `verify.py` gate (assumes `output/` already built) |
| `make clean` | remove `__pycache__` / `.ruff_cache` / `.mypy_cache` |

Note `make smoke` runs against whatever `config.yaml` + `work/` are in the repo root, so use it for real runs (or run it from inside a scratch dir). For a no-touch demo, use the scratch-dir block above. The **devcontainer** ([.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json)) gives you Python 3.12 + the GitHub CLI with deps pre-installed via `postCreateCommand` — open the repo in it and skip straight to `make compile` or the scratch-dir smoke.

---

**Next:** [02-concepts.md](02-concepts.md) for the mental model (mechanical vs. judgement split, why it runs on cheap models), then [03-architecture.md](03-architecture.md) and [04-engine.md](04-engine.md). Full suite index: [README.md](README.md).
