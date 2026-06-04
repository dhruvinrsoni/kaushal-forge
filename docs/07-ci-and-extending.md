# CI, Testing & Extending KaushalForge

**Who/what:** For a contributor maintaining or extending the engine — how CI gates every change, how to run the render-smoke safely on your own machine, and how to add styles, phases, role variants, and page-fit tuning without breaking the verify gate.

🔒 KaushalForge is proprietary and private (All Rights Reserved — see [LICENSE](../LICENSE)). It is not open source. Everything below assumes you are an authorized maintainer; do not invite external contribution or publish the package.

---

## CI: two jobs in [.github/workflows/ci.yml](../.github/workflows/ci.yml)

CI runs on every push and pull request to `main`. Permissions are read-only (`contents: read`). There are two jobs.

### Job 1 — `lint-validate` (fast, mostly advisory)

Runs on `ubuntu-latest`, Python 3.12, installs `ruff pyyaml pypdf`, then three steps:

1. **Compile-check the engine** — `python -m py_compile engine/*.py`. This is a hard failure: any syntax error in an engine script fails the job.
2. **Lint (non-blocking for now)** — `ruff check engine || true`. The `|| true` means lint findings are **advisory** and will not fail CI today. Treat clean `ruff` output as a courtesy, not a gate; see [pyproject.toml](../pyproject.toml) for the rule set (`E, F, I, N, UP, B, SIM, TCH`, line length 100, target py310).
3. **Validate JSON** — an inline Python heredoc `json.load`s every file matched by three globs and exits non-zero if any is invalid:
   - `.github/skills/kaushal-forge/schemas/*.json`
   - `.github/skills/kaushal-forge/examples/*.json`
   - `tests/fixtures/**/*.json` (recursive)

   So if you edit a schema, a gold example, or a fixture and leave trailing-comma / bad-JSON breakage, this step catches it.

### Job 2 — `render-smoke` (the real gate)

This is the job that proves the engine still produces correct, leak-free, correctly-paginated PDFs. Steps (see ci.yml:43-70):

1. Checkout, Python 3.12, `pip install pyyaml pypdf`.
2. **Install Tectonic** via `wtfjoke/setup-tectonic@v3` (the LaTeX engine; uses `GITHUB_TOKEN`).
3. **Stage anonymized fixtures** — this is the important part. CI copies the fictional fixtures into the live runtime locations:
   ```bash
   cp tests/fixtures/config.yaml ./config.yaml
   mkdir -p work
   cp tests/fixtures/*.json work/
   [ -d tests/fixtures/strategy ] && cp -r tests/fixtures/strategy work/strategy || true
   ```
4. **Render + build + verify**:
   ```bash
   python engine/render_resumes.py
   python engine/render_coverletters.py
   python engine/render_linkedin.py
   python engine/render_strategy.py
   export CAREERFORGE_TECTONIC="$(which tectonic)"
   python engine/build_pdfs.py
   python engine/verify.py
   ```

`engine/verify.py` is the gate: if it exits non-zero, the job (and the PR) fails. Note CI runs on a fresh, ephemeral checkout, so `cp ... ./config.yaml` is harmless there — **on your own machine it would clobber your live config**, which is why you must run the smoke in a scratch dir (next section).

---

## The fixtures: a complete fictional run

Everything under [tests/fixtures/](../tests/fixtures/) is a fully fictional persona — **Asha Verma** at Acme Cloud Technologies / Globex Systems / Initech Labs, with open-source projects PromptForge, QuickLog, AgentKit. There is no real career data anywhere in the repo, and there must never be.

| Fixture | Feeds | Role |
|---|---|---|
| [config.yaml](../tests/fixtures/config.yaml) | staged to `./config.yaml` | person/contact, `accent_hex: 1F4E79`, `two_page: "all"`, `cap_overrides: {"01": 4}`, and three `verify.mask` |
| [profile.json](../tests/fixtures/profile.json) | `work/profile.json` | master KB → the `09-master-2page` résumé + education/certs/contact |
| [variants.json](../tests/fixtures/variants.json) | `work/variants.json` | two role variants, **ids `01` and `03`** (backend, AI/GenAI) |
| [letters.json](../tests/fixtures/letters.json) | `work/letters.json` | matching cover letters for ids `01` and `03` |
| [linkedin.json](../tests/fixtures/linkedin.json) | `work/linkedin.json` | LinkedIn rewrite (headlines / about — also the source for the char-limit check) |
| [strategy/career-strategy.md](../tests/fixtures/strategy/career-strategy.md) | `work/strategy/` | copied through by `render_strategy.py` |

The fixtures are **deliberately sized** so the page-count gate is meaningful:

- Each role variant (`01-...`, `03-...`) is capped on the 1-page edition to land at exactly **1 page**. The current-role bullet cap comes from `cap_overrides` (`01` → 4) defaulting to 4 (render_resumes.py:171), then `[cap0, 2, 2] + [1]*8` across the rest of the experience list.
- Because `two_page: "all"`, every variant also gets a full-depth `-2page` edition that must land at exactly **2 pages**, and the master `09-master-2page` is always 2 pages. These 2-page editions exercise the dense **twocol** style, which uses `paracol` so it page-breaks cleanly across two columns (see [cf-twocol.tex](../engine/templates/styles/cf-twocol.tex)).
- The fixture's three placeholder leak-scan terms (fictional codenames defined in `tests/fixtures/config.yaml`) do **not** appear in any fixture content, so the scan exercises its logic and passes cleanly.

The whole run must end in `VERIFY OK`. The fixture config carries an exception in [.gitignore](../.gitignore):L13 — `!tests/fixtures/config.yaml` — so this one config is tracked even though the live root `config.yaml` is ignored everywhere.

---

## Running the smoke locally (safely)

The smoke overwrites `./config.yaml` and `work/`. **Never run it from a checkout that holds a live person's config/work/output** — you will clobber real data and risk committing PDFs. Always use a throwaway clone in a scratch directory:

```bash
# 1. Clone (or copy) the repo into a scratch dir that has NO live run in it
git clone <repo-url> /tmp/kf-smoke
cd /tmp/kf-smoke

# 2. Make sure Tectonic is available
python engine/bootstrap.py        # downloads Tectonic to engine/.bin + writes engine/.tectonic_path
# ...or point at an existing binary:
export CAREERFORGE_TECTONIC="$(which tectonic)"

# 3. Stage the fixtures exactly like CI does
cp tests/fixtures/config.yaml ./config.yaml
mkdir -p work
cp tests/fixtures/*.json work/
cp -r tests/fixtures/strategy work/strategy

# 4. Render -> build -> verify
make smoke
```

`make smoke` runs the four renderers, then `build_pdfs.py`, then `verify.py` (see the Makefile target list below). A green run prints the per-file page-count table from `build_pdfs.py` and ends with `VERIFY OK`.

If you only want to re-check an already-built `output/`, run `make verify` (just the gate). To start over, `git clean -xdf` the scratch clone or delete it.

> Working in your real run directory and just want to confirm a change? Stash your live `config.yaml`/`work/`/`output/` first, or — better — clone fresh. The renderers always read from `./config.yaml` + `work/` and always write to `output/` relative to repo root; there is no override flag.

---

## Makefile targets

The [Makefile](../Makefile) is the canonical local entry point:

| Target | What it does |
|---|---|
| `make dev` | `pip install pyyaml pypdf ruff` — engine runtime deps + lint tooling |
| `make lint` | `ruff check engine` (here it is *not* `\|\| true`, so it returns non-zero locally) |
| `make format` | `ruff format engine` |
| `make compile` | `python -m py_compile engine/*.py` — fast byte-compile sanity check |
| `make smoke` | full pipeline: four renderers → `build_pdfs.py` → `verify.py` |
| `make verify` | just the `verify.py` gate (assumes `output/` already built) |
| `make clean` | remove `.ruff_cache .mypy_cache __pycache__ engine/__pycache__` |
| `make all` | `compile lint` |

Note: `make smoke` does **not** stage fixtures or set `CAREERFORGE_TECTONIC` for you — do steps 2-3 above first.

---

## How to extend

### Add a LaTeX style

The three résumé styles are wired in two places in [engine/render_resumes.py](../engine/render_resumes.py):

- `copy_styles()` (render_resumes.py:131) copies the source files `("cf-ats.tex", "cf-modern.tex", "cf-twocol.tex")` from `engine/templates/styles/` into `output/Resumes/_styles/`, injecting `accent_hex` into modern/twocol via the `\definecolor{accent}{HTML}{...}` regex.
- `write_folder()` (render_resumes.py:125) writes one `build-<style>.tex` driver per style in the tuple `("ats", "modern", "twocol")`, each `\input`-ing `../_styles/cf-<style>.tex` via `driver()`.

To add a style `cf-<style>.tex`:

1. Create `engine/templates/styles/cf-<style>.tex`. Follow the existing contract — it must define the macros the generated `content.tex` calls: `\Name`, `\Headline`, `\Contact`, `\Summary`, optional `\FocusData`, `\SkillsData`/`\SkillRow`, `\ExperienceData`/`\Role`/`Achvs`/`\Achv`, optional `\ProjectsData`/`\Project`, `\EducationData`/`\EduItem`, `\ExtrasData`/`\Cred`, and `\BuildResume`. Copy one of the existing styles as your skeleton.
2. Add the source filename to the `copy_styles()` tuple and the bare style name to the `write_folder()` tuple. Keep them in sync.
3. If you want the accent color injected, include a `\definecolor{accent}{HTML}{XXXXXX}` line so the regex can rewrite it.
4. Re-run the smoke; confirm `build_pdfs.py` compiles the new `build-<style>.pdf` for every folder and `verify.py` still passes.

Cover letters use a single style, `cf-letter.tex`, wired separately in [engine/render_coverletters.py](../engine/render_coverletters.py) (`copy_style()` / `letter_tex()` hardcode `cf-letter.tex` at 11pt).

### Add or adjust an AI phase

Phases are model-driven content generation, defined in lockstep across three trees:

- `.github/skills/kaushal-forge/phases/PN-*.md` — the Claude-skill phase instruction.
- `prompts/PN-*.md` — the portable copy-paste prompt for non-Claude models.
- `.github/skills/kaushal-forge/schemas/*.schema.json` — the rigid JSON contract the phase must fill.
- `.github/skills/kaushal-forge/examples/*` — the worked gold example beside the schema.

Current phases are `P1-structure` → `P6-strategy` (profile, targeting, LinkedIn, resumes, cover letters, strategy). To add or change one: edit the matching `phases/PN`, `prompts/PN`, schema, and example **together**; keep the JSON example valid (the `lint-validate` JSON step will catch invalid JSON). If a phase produces a new `work/*.json`, add a renderer or extend an existing one to consume it, and add a fixture so CI exercises the new path. Keep every example/fixture fictional (Asha Verma persona only).

### Add a role variant

A role variant is just a new object in `variants.json` (and usually a paired object in `letters.json` with the same `id`/`key`). Each variant object needs at minimum: `id`, `key`, `headline`, `summary`, optional `focus`, `skills_rows` (label/items), `experience` (role/org/dates/location/bullets), optional `projects`, and `guide_md`. The renderer keys folder names off `<id>-<key>` and reserves `09` for the master (render_resumes.py:163-167 skip any object with `id == "09"`).

- 1-page edition: built for every non-`09` variant, capped (`cap_overrides[id]` or 4 for the current role).
- 2-page edition: built only if `id` is in `config.resume.two_page` (or always, when `two_page: "all"`).

When you add a variant to the fixtures, size its bullets so the 1-page edition fits 1 page and (if it gets a 2-page edition) the 2-page fills 2 — otherwise the page-count gate fails.

### Tune page fit via config

You rarely touch code for fit; tune [config.yaml](../config.example.yaml) instead:

- **`resume.cap_overrides`** — per-id current-role bullet cap on the 1-page edition (e.g. `"05": 3`). Lower it when a dense, long-bullet variant spills to a second page.
- **`resume.two_page`** — `"all"` to give every variant a 2-page edition, or an explicit list like `["05","06","07"]` to limit which ids get one.
- **`resume.accent_hex`** — heading/name color for modern/twocol/letter (ATS stays black).

---

## Run-for-a-new-person checklist

This is the contributor's view of an end-to-end run (the operator's steps live in [RUNBOOK.md](../RUNBOOK.md); the why is in [MASTER-PLAN.md](../MASTER-PLAN.md)). Do this in a **clean** working tree:

1. `python engine/bootstrap.py` — deps + Tectonic.
2. `cp config.example.yaml config.yaml` and fill `person` / `contact` / `targets` / `verify.mask`.
3. Drop the person's raw data into `inbox/`, then `python engine/intake_dump.py` → `work/00-raw-dump.txt`.
4. Run phases P1→P6 (skill or `prompts/`) → `work/{profile,linkedin,variants,letters}.json` + `work/strategy/`.
5. `python engine/render_{resumes,coverletters,linkedin,strategy}.py`.
6. `python engine/build_pdfs.py` (page-count table), then `python engine/verify.py` (must print `VERIFY OK`).
7. Outputs land in `output/`. **Never commit** any of `config.yaml`, `work/`, `output/`, or `*.pdf`.

**Refresh later:** the renderers are re-runnable. Update the relevant `work/*.json` (or hand-edit a `content.tex`) and re-run renderers → build → verify. Set `config.verify.mask` *before* re-running so the leak gate covers any newly added employer/client/codename.

---

## Troubleshooting

### `verify.py` failures (the gate, [engine/verify.py](../engine/verify.py))

`verify.py` prints `VERIFY FAILED (N):` and a bulleted list. Match the prefix:

| Failure | Meaning | Fix |
|---|---|---|
| `LEAK '<term>' in ...` | a `verify.mask` string appears (case-insensitive) in a rendered output / `content.tex` | remove the term from the source JSON/content and re-render; or remove it from `forbidden_terms` only if it was a false positive |
| `ENTITY '&gt;' / '&amp;' / ...` | a raw HTML entity leaked into output text | fix the source JSON — the renderers' `esc()`/`deent()` already un-escape entities, so a leak means the entity reached a path that wasn't sanitized; correct the JSON value |
| `HEADLINE N>220` / `ABOUT[...] N>2600` | a LinkedIn headline >220 chars, or `about.primary`/`about.alt` >2600 chars (read from `work/linkedin.json`) | shorten the offending field in `linkedin.json` and re-render |
| `PAGES <folder>/build-*.pdf = N (want M)` | a résumé PDF has the wrong page count (role/2-page editions expect 1; `*-2page` and `09-master-*` expect 2) | adjust content volume or `cap_overrides`/`two_page` so the page count matches |
| `PAGES letter ... = N (want 1)` | a cover-letter PDF is not exactly 1 page | trim the letter body in `letters.json` |

The page-count check needs `pypdf`; without it the check is skipped (`note: pypdf not installed`), so install it (`make dev`) before trusting a green run locally.

### Tectonic not found

`build_pdfs.py` resolves Tectonic in order (build_pdfs.py:8-19): `CAREERFORGE_TECTONIC` env var → `engine/.tectonic_path` → `tectonic` on `PATH` → `engine/.bin/tectonic[.exe]`. If none resolve it prints `ERROR: Tectonic not found. Run: python engine/bootstrap.py ...` and exits 2. Fix by running `python engine/bootstrap.py` (downloads to `engine/.bin` and writes `engine/.tectonic_path`) or `export CAREERFORGE_TECTONIC="$(which tectonic)"`. As a last resort, the generated `build-*.tex` drivers compile on Overleaf. Note `engine/.bin/` and `engine/.tectonic_path` are gitignored — never commit the binary.

### Page count off but no content bug

If a 1-pager spills, lower its `cap_overrides[id]`; if a 2-page edition under/overflows, adjust the variant's bullet/skill volume. The fixtures are tuned exactly this way — they are the reference for "how much content fits."

---

## 🔒 Proprietary & privacy do's and don'ts

**Never commit:**
- `config.yaml`, `inbox/*`, `work/*`, `output/*`, or any `*.pdf` — all gitignored (see [.gitignore](../.gitignore); folders kept via `.gitkeep`).
- Any real personal/career data, employer/client names, or internal codenames — these belong in `config.verify.mask` (gitignored), not in tracked files.
- The Tectonic binary (`engine/.bin/`) or `engine/.tectonic_path` (machine-specific, gitignored).

**Leak gate (defense-in-depth):** `config.verify.mask` (term → replacement) is the single source of truth. `verify.py` scans outputs **and tracked source** for those terms; a pre-commit hook (`.githooks/`, installed by `bootstrap.py`) blocks any commit that stages one (text or PDF). So a sensitive term can't reach a commit or an output.

**Always:**
- Keep every example (`.github/skills/kaushal-forge/examples/`) and fixture (`tests/fixtures/`) **fully fictional** — Asha Verma / Acme Cloud / Globex / Initech / PromptForge / QuickLog / AgentKit only.
- Treat the package as **non-publishable**: `pyproject.toml` sets `LicenseRef-Proprietary`, the `Private :: Do Not Upload` classifier, and `py-modules = []` to block accidental packaging. There is intentionally **no PyPI publish workflow** — do not add one.

---

**Next:** back to the [README.md](README.md) index, or revisit the engine internals in [04-engine.md](04-engine.md) and the JSON contracts in [06-data-contracts.md](06-data-contracts.md).
