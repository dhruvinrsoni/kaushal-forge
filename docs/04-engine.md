# Engine internals (code-level)

**Who/what:** the deepest doc in the suite — a top-to-bottom code reading of every script in [engine/](../engine/) for a developer who wants to know exactly what each line does. Read [03-architecture.md](03-architecture.md) first for the data flow and [06-data-contracts.md](06-data-contracts.md) for the JSON shapes the renderers consume.

> 🔒 Proprietary, author-owned. This is private internal documentation; nothing here is open source.

The engine is deliberately model-agnostic: the AI phases write JSON into `work/`, and these scripts do **pure deterministic rendering + verification** with no network calls and no LLM dependency. Every script is re-runnable; hand-edits to generated `content.tex` survive unless you re-render. Common pattern at the top of each file is `HERE = os.path.dirname(os.path.abspath(__file__))` and `ROOT = os.path.dirname(HERE)` to resolve paths relative to the repo root regardless of cwd.

---

## 1. `bootstrap.py` — one-time setup

[engine/bootstrap.py](../engine/bootstrap.py) installs Python deps and resolves (or downloads) the Tectonic LaTeX engine. Key constants ([bootstrap.py:6-8](../engine/bootstrap.py)):

```python
HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, ".bin")
PATHFILE = os.path.join(HERE, ".tectonic_path")
```

`main()` ([bootstrap.py:54-67](../engine/bootstrap.py)) runs three steps:

1. **`pip_install()`** ([bootstrap.py:10-16](../engine/bootstrap.py)) — iterates `("pypdf", "pyyaml")`, attempts `__import__("yaml" if pkg == "pyyaml" else pkg)`, and on `ImportError` shells out to `subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", pkg])`. Note the import-name remap: the package `pyyaml` is probed as the module `yaml`.
2. **`existing_tectonic()`** ([bootstrap.py:18-24](../engine/bootstrap.py)) — checks candidates in order: `$CAREERFORGE_TECTONIC` env var, `shutil.which("tectonic")` (PATH), `.bin/tectonic.exe`, `.bin/tectonic`, then `~\AppData\Local\tectonic\tectonic.exe`. Returns the first that exists.
3. **`download_tectonic()`** ([bootstrap.py:32-52](../engine/bootstrap.py)) — only called if no existing binary. Hits the GitHub API (`releases/latest`) with a `User-Agent: kaushal-forge` header, picks the asset matching the current platform via `asset_filter()` ([bootstrap.py:26-30](../engine/bootstrap.py)) — Windows wants `*x86_64-pc-windows-msvc.zip`, macOS wants `apple-darwin*.tar.gz`, else gnu-linux `linux*.tar.gz` — downloads with `urllib.request.urlretrieve`, extracts (`zipfile` for `.zip`, `tarfile` otherwise) into `.bin`, then walks the tree for a file named `tectonic`/`tectonic.exe`.

The resolved path is written to **`engine/.tectonic_path`** ([bootstrap.py:64](../engine/bootstrap.py)) so the other scripts don't have to re-resolve. If the download fails, it does **not** raise — it prints a WARN and returns, leaving the Overleaf fallback (compile the `build-*.tex` files manually) as the escape hatch. The repo already ships a populated `engine/.tectonic_path`.

---

## 2. `intake_dump.py` — inbox concatenation

[engine/intake_dump.py](../engine/intake_dump.py) walks `inbox/` recursively and concatenates everything readable into `work/00-raw-dump.txt`, the single text blob the AI intake phase reads.

- **`read_text(p)`** ([intake_dump.py:9-25](../engine/intake_dump.py)) branches on extension:
  - `.txt .md .csv .json .log .tex` → read directly as UTF-8 with `errors="replace"`.
  - `.pdf` → `import pypdf` and join `pg.extract_text() or ""` across pages; returns `None` on any exception.
  - `.docx` → `import docx` (python-docx) and join paragraph text; returns `None` if the lib is missing.
  - anything else → `None`.
- **`main()`** ([intake_dump.py:27-46](../engine/intake_dump.py)) globs `inbox/**/*` recursively (`sorted`, files only), **skips `.gitkeep`**, calls `read_text` per file, and for readables appends a delimited block: `\n\n=== FILE: {rel} ===\n{txt}` where `rel` is the path relative to `inbox/`. Files returning `None` go to a `skipped` list and are printed with a "paste their text manually and re-run" note. Empty inbox prints guidance to add LinkedIn data exports, performance reviews, resumes, etc.

This script never fails on unreadable input — it degrades to a skip list, keeping the pipeline moving.

---

## 3. `render_resumes.py` — the core renderer (in depth)

[engine/render_resumes.py](../engine/render_resumes.py) is the largest and most important script. It turns `config.yaml` + `work/profile.json` + `work/variants.json` into per-variant folders under `output/Resumes/`.

### 3.1 Inputs and loaders

- **`load_config()`** ([render_resumes.py:24-27](../engine/render_resumes.py)) — lazy `import yaml`, `yaml.safe_load` of `config.yaml`.
- **`profile`** ([render_resumes.py:140](../engine/render_resumes.py)) — `work/profile.json`, the structured knowledge base. Source of the always-built Master and of shared `education`/`certs`/`awards`/`languages`.
- **`variants`** ([render_resumes.py:141-143](../engine/render_resumes.py)) — `work/variants.json`. If the top level is a dict (a model wrapped it), it tolerantly unwraps `results` then `variants`.

### 3.2 `esc()` — the LaTeX escaping pipeline (exact order matters)

[render_resumes.py:29-43](../engine/render_resumes.py). Applied to **every** user/AI-supplied string before it reaches LaTeX. The order is load-bearing:

1. **HTML-entity decode first** ([line 31](../engine/render_resumes.py)): `&gt;→>`, `&lt;→<`, `&amp;→&`, `&#39;→'`, `&quot;→"`. This runs before LaTeX escaping so that a decoded `&` is then properly escaped to `\&` in the next step (and so `verify.py`'s entity scan never sees residual entities in output).
2. **Backslash** ([line 32](../engine/render_resumes.py)): `\` → `\textbackslash{}`. Must be first among LaTeX specials, otherwise the backslashes introduced by later substitutions would be double-escaped.
3. **The five specials** ([line 33](../engine/render_resumes.py)): `&→\&`, `%→\%`, `#→\#`, `_→\_`.
4. **Dollar** ([line 34](../engine/render_resumes.py)): `$→\$`.
5. **Arrow** ([line 35](../engine/render_resumes.py)): the literal `->` → `$\rightarrow$`. (Runs after `$` escaping so the math `$` it emits is intentional and not re-escaped.)
6. **Tilde** ([line 36](../engine/render_resumes.py)): `~` → `\textasciitilde{}`.
7. **Smart quotes** ([lines 37-42](../engine/render_resumes.py)): a single pass toggling a boolean `openq` — alternating `"` becomes `` `` `` (open) then `''` (close).

`render_coverletters.py` carries a **byte-identical** `esc()` ([render_coverletters.py:16-30](../engine/render_coverletters.py)) so letters and resumes escape the same way.

### 3.3 Helper renderers

- **`contact_line(cfg)`** ([render_resumes.py:45-54](../engine/render_resumes.py)) — builds a `\textbullet{}`-joined line. Email/linkedin/github/portfolio become `\href{...}` links (linkedin/github/portfolio get an `https://` prefix the config intentionally omits); phone and `location_display` go through `esc()`.
- **`edu_items(profile, full)`** ([render_resumes.py:56-62](../engine/render_resumes.py)) — emits `\EduItem{degree}{institution}{dates}{detail}`. The `detail` field is **only included when `full=True`** (2-page); on the 1-pager it is blank. Falls back to `\EduItem{}{}{}{}` if there is no education.
- **`extras_block(profile, full)`** ([render_resumes.py:64-79](../engine/render_resumes.py)) — two modes. **Full**: separate `\Cred{}` lines for certifications and an awards/languages tail. **Compact (1-page)**: a single `\Cred{}` joining at most `certs[:3]`, only the **first** award (`awards[0]`), and languages.
- **`render_skills(rows)`** ([render_resumes.py:87-88](../engine/render_resumes.py)) — one `\SkillRow{label}{items}` per row.
- **`render_experience(exp, caps)`** ([render_resumes.py:90-99](../engine/render_resumes.py)) — for each role at index `ix`, takes `cap = caps[ix] if ix < len(caps) else 1`. If `cap is None`, **all** bullets; otherwise `bullets[:cap]`. Emits `\Role{role}{org}{dates}{location}` then an `Achvs` itemize of `\Achv{...}`.
- **`render_projects(projs)`** ([render_resumes.py:101-102](../engine/render_resumes.py)) — one `\Project{name}{meta}{desc}` per entry.

### 3.4 `assemble()` — the macro emission contract

[render_resumes.py:104-119](../engine/render_resumes.py). Produces the style-agnostic `content.tex` by emitting semantic macros in a fixed order:

```
\Name{...}  \Headline{...}  \Contact{...}  \Summary{...}
\FocusData{...}        # only if focus is non-empty/non-blank
\SkillsData{% ... }
\ExperienceData{% ... }
\ProjectsData{% ... }  # only if proj_tex.strip() is non-empty
\EducationData{% ... }
\ExtrasData{% ... }
\BuildResume
```

`\FocusData` and `\ProjectsData` are **conditionally emitted** ([lines 110-115](../engine/render_resumes.py)); the styles also defend against absence via `\ifx...\empty` guards (see §6). `\BuildResume` (the last line) is what actually lays out the document — `content.tex` itself contains no layout.

### 3.5 The Master (09) — always built, 2-page

[render_resumes.py:150-160](../engine/render_resumes.py). Built straight from `profile.json` (not from variants), with **all bullets** (`m_caps = [None] * len(experience)`), full education detail and full extras. Headline falls back from `profile["headline"]` to `profile["identity"]["tagline"]`. Written to `output/Resumes/09-master-2page/` at **`10pt`**. This folder always exists regardless of what variants the AI produced.

### 3.6 Role variants — the 1-page cap policy vs the 2-page full edition

[render_resumes.py:162-196](../engine/render_resumes.py). Variants with `id == "09"` are skipped (Master is built separately, [lines 163, 167-168](../engine/render_resumes.py)). For each remaining variant, `key = v.get("key", vid)` and folder name is `<id>-<key>` ([line 178](../engine/render_resumes.py)).

**1-page (capped), `9pt`** ([lines 170-182](../engine/render_resumes.py)):

- Current-role cap `cap0 = int(cap_over.get(vid, 4))` — default **4**, overridable per-id via `resume.cap_overrides` (e.g. `"05": 3` in [config.example.yaml](../config.example.yaml)).
- Full cap vector: `caps_1p = [cap0, 2, 2] + [1] * 8` — so role 0 gets `cap0` bullets, roles 1 and 2 get 2 each, all later roles get 1 (the `render_experience` index-overflow fallback also yields 1).
- Skills truncated to `skills_rows[:4]`; projects truncated to `projects[:2]`.
- Education/extras rendered in **compact** mode (`full=False`).
- Driver point size **`9pt`** with `extarticle` (extended article class lets you go below 10pt cleanly).
- A `GUIDE.md` is written from `v.get("guide_md", "")`.

**2-page (full), `10pt`** ([lines 184-196](../engine/render_resumes.py)) — built only if `vid in tp_set`:

- `tp_set` is computed from `resume.two_page` ([line 164](../engine/render_resumes.py)): if `"all"`, it's every non-09 role id; otherwise the configured list (stringified).
- `caps_full = [None] * len(experience)` → all bullets; full skills (no `[:4]`); all projects; full education/extras.
- Folder `<id>-<key>-2page`, driver `10pt`, and a generated `GUIDE.md` cross-referencing `../<id>-<key>/GUIDE.md`.

### 3.7 `write_folder()` and `driver()`

- **`driver(style, pt)`** ([render_resumes.py:81-85](../engine/render_resumes.py)) — emits a tiny main document: `\documentclass[letterpaper,<pt>]{extarticle}`, `\input{../_styles/cf-<style>.tex}`, then `\input{content.tex}`. So one `content.tex` is shared by three drivers.
- **`write_folder(folder, content, pt)`** ([render_resumes.py:121-127](../engine/render_resumes.py)) — writes `content.tex` plus **three** build files: `build-ats.tex`, `build-modern.tex`, `build-twocol.tex`. Each variant folder therefore compiles to three PDFs from the same content.

### 3.8 `copy_styles()` — accent-hex injection

[render_resumes.py:129-136](../engine/render_resumes.py). Copies `cf-ats.tex`, `cf-modern.tex`, `cf-twocol.tex` into `output/Resumes/_styles/`. If `resume.accent_hex` is set, a regex rewrites the accent color in each style:

```python
re.sub(r"(\definecolor\{accent\}\{HTML\}\{)[0-9A-Fa-f]{6}(\})", r"\g<1>%s\g<2>" % accent_hex, txt)
```

Because `cf-ats.tex` has **no `\definecolor{accent}`** (see §6), the regex matches nothing there and the ATS style stays black — exactly as `config.example.yaml` documents.

---

## 4. `render_coverletters.py`

[engine/render_coverletters.py](../engine/render_coverletters.py). Consumes `work/letters.json` (same tolerant `results`/`letters` unwrap, [lines 85-86](../engine/render_coverletters.py)) and writes `output/CoverLetters/<id>-<key>/` plus the shared `_styles/cf-letter.tex`.

- **`deent(s)`** ([lines 32-34](../engine/render_coverletters.py)) — a lighter sibling of `esc()` that **only** decodes HTML entities (no LaTeX escaping). It is applied in `main()` ([lines 90-92](../engine/render_coverletters.py)) to the markdown-bound fields (`email_subject`, `opening`, `closing`, `why_company_prompt`, `notes_md`, and each `body` paragraph) so the `.md` output is clean of entities. The `.tex` path re-escapes those same strings through `esc()`.
- **`letter_tex(v, cfg)`** ([lines 53-70](../engine/render_coverletters.py)) — emits an `article` at `11pt`, `\input{../_styles/cf-letter.tex}`, then the macro contract: `\Name`, `\Contact`, `\LetterDate{[Date]}`, `\Recipient{Hiring Team, [Company]...}`, `\Subject{Re: [Role] --- Application}`, `\Greeting`, then `\LetterBody{ \Para{opening} \Para{body...} \Fill{...} \Para{closing} }`, `\Signoff{Sincerely,}`, `\BuildLetter`. The bracketed `[Company]`/`[Role]`/`[Date]` and the **`\Fill{...}` placeholder** ([line 67](../engine/render_coverletters.py)) are intentional fill-me-in markers; `\Fill` renders in accent italic so it's visually obvious (see §6).
- **`letter_md(v, cfg)`** ([lines 72-80](../engine/render_coverletters.py)) — a paste-ready markdown version with the same bracketed placeholders, a `> why_company_prompt` blockquote, a Notes section, and an explicit "Fill before sending" checklist.
- **`copy_style()`** ([lines 46-51](../engine/render_coverletters.py)) — same accent-hex regex injection as resumes, applied to `cf-letter.tex`.

`contact_line()` here ([lines 36-44](../engine/render_coverletters.py)) differs slightly from the resume version: it splits `location_display` on `|` and keeps only the first segment, dropping the "Open to relocation" tail that a letter doesn't need.

---

## 5. `render_linkedin.py`, `render_strategy.py`, `build_pdfs.py`, `verify.py`

### 5.1 `render_linkedin.py`

[engine/render_linkedin.py](../engine/render_linkedin.py). Reads `work/linkedin.json` and writes **eight** section files into `output/LinkedIn/` ([lines 17-61](../engine/render_linkedin.py)): `00-overview.md` (always, with the apply-order and limits cheat sheet), then conditionally `01-headline.md`, `02-about.md`, `03-experience.md`, `04-skills.md`, `05-featured-and-projects.md`, `06-certs-education-awards.md`, `07-misc-settings.md` — each guarded by the presence of its source key, so it's tolerant of partial input. **Live character counts** are computed inline with `len(...)` for each headline variant ([line 24](../engine/render_linkedin.py)) and the about primary/alt ([lines 29-30](../engine/render_linkedin.py)); these are display-only — the hard limits are enforced separately by `verify.py`.

### 5.2 `render_strategy.py`

[engine/render_strategy.py](../engine/render_strategy.py). The simplest renderer: copies `work/strategy/*.md` verbatim into `output/Strategy/` ([lines 9-11](../engine/render_strategy.py)) and writes a `00-index.md` with a bullet link per copied doc ([line 12](../engine/render_strategy.py)). Pure passthrough plus index.

### 5.3 `build_pdfs.py`

[engine/build_pdfs.py](../engine/build_pdfs.py). Compiles every resume `build-*.tex` and every cover-letter `letter.tex` with Tectonic.

- **`tectonic()` resolution order** ([lines 8-19](../engine/build_pdfs.py)) — the canonical lookup the whole engine relies on:
  1. `$CAREERFORGE_TECTONIC` (if it exists on disk),
  2. `engine/.tectonic_path` (read, stripped, must exist),
  3. `shutil.which("tectonic")` (PATH),
  4. `engine/.bin/tectonic.exe` then `engine/.bin/tectonic`.
  Returns `None` if none found → `main()` prints an error pointing at `bootstrap.py`/Overleaf and `sys.exit(2)` ([lines 30-32](../engine/build_pdfs.py)).
- **Compile loop** ([lines 33-44](../engine/build_pdfs.py)) — globs `output/Resumes/*/build-*.tex` + `output/CoverLetters/*/letter.tex`, and for each runs `subprocess.run([tec, basename], cwd=folder, capture_output=True)`. Success requires both `returncode == 0` **and** the `.pdf` exists. Prints a `file / exit / pages` table; `pages()` ([lines 21-26](../engine/build_pdfs.py)) uses `pypdf` and degrades to `"?"` on error.
- **Exit code** ([lines 45-46](../engine/build_pdfs.py)) — `sys.exit(1 if fail else 0)`, so a single failed compile fails the run.

### 5.4 `verify.py` — the gate (four checks)

[engine/verify.py](../engine/verify.py). Accumulates failures into a `fails` list and, if non-empty, prints them and `sys.exit(1)` ([lines 61-65](../engine/verify.py)). This is the **gate**: non-zero exit is the contract.

1. **Forbidden-terms leak scan** ([lines 22-34](../engine/verify.py)) — lowercases `config.verify.forbidden_terms` (internal codenames, client/manager/peer names that must never surface) and scans, case-insensitively, every `Resumes/*/content.tex`, `CoverLetters/*/letter.{tex,md}`, `LinkedIn/*.md`, and `Strategy/*.md`. Any hit → `LEAK '<term>' in <file>`.
2. **HTML-entity scan** ([lines 23, 34-35](../engine/verify.py)) — over the same file set, flags any of `&gt; &lt; &amp; &#39; &quot;` that survived rendering → `ENTITY '<e>' in <file>`. This is the backstop for `esc()`/`deent()`.
3. **LinkedIn char limits** ([lines 38-45](../engine/verify.py)) — read from `work/linkedin.json`: each `headline_variants[].text` must be **≤ 220**; `about.primary` and `about.alt` must each be **≤ 2600**.
4. **PDF page counts** ([lines 48-57](../engine/verify.py)) via `pypdf` (skipped with a note if pypdf is missing, [lines 58-59](../engine/verify.py)):
   - Resume PDFs: `want = 2 if folder.endswith("2page") or folder.startswith("09") else 1` — so role variants must be exactly **1 page**, and every `*-2page` plus the `09` Master must be exactly **2 pages**.
   - Cover letters: `letter.pdf` must be exactly **1 page**.

If everything passes it prints `VERIFY OK ...`.

---

## 6. The LaTeX macro contract and the four styles

Every `content.tex`/`letter.tex` is **style-agnostic**: it only emits semantic macros (`\Name`, `\Role`, `\SkillRow`, `\BuildResume`, …). The chosen style file *defines* those macros, so swapping `build-ats.tex` → `build-modern.tex` re-typesets identical content with zero content changes. All three resume styles declare the **same macro set** ([cf-ats.tex:25-52](../engine/templates/styles/cf-ats.tex), mirrored in modern/twocol) and the same `\ifx\res...\empty` guards so conditionally-omitted sections (Summary, Focus, Projects, Skills, Extras) simply don't render.

| Style | File | Layout | Accent? |
|---|---|---|---|
| `ats` | [cf-ats.tex](../engine/templates/styles/cf-ats.tex) | single-column, ATS-safe | **No** — `\definecolor{rule}{gray}{0.0}` only; stays black |
| `modern` | [cf-modern.tex](../engine/templates/styles/cf-modern.tex) | single-column with accent rules/bullets | Yes — `\definecolor{accent}{HTML}{1F4E79}` |
| `twocol` | [cf-twocol.tex](../engine/templates/styles/cf-twocol.tex) | sidebar + main via `paracol` | Yes |
| `letter` | [cf-letter.tex](../engine/templates/styles/cf-letter.tex) | cover letter | Yes |

- **`ats`** ([cf-ats.tex](../engine/templates/styles/cf-ats.tex)) — Helvetica/sans, tight `geometry` (0.42in top/bottom, 0.5in sides), `\rsection` draws a plain black rule, bullets are `\textbullet`. Crucially it has **no `accent` color**, so `copy_styles()`'s regex can't touch it — ATS PDFs are always pure black single-column for maximum parser compatibility.
- **`modern`** ([cf-modern.tex](../engine/templates/styles/cf-modern.tex)) — same single-column skeleton plus `accent`/`accentlt`/`ink` colors. `\rsection` ([lines 41-45](../engine/templates/styles/cf-modern.tex)) prepends an accent tab rule and colors the heading; role dates, project names, education dates and the name are accent-colored; bullets are accent.
- **`twocol`** ([cf-twocol.tex](../engine/templates/styles/cf-twocol.tex)) — adds `\usepackage{paracol}` and lays `\BuildResume` ([lines 60-79](../engine/templates/styles/cf-twocol.tex)) into a `columnratio{0.34}` two-column body: **sidebar** = Skills, Education, Certifications & Recognition; **main** (`\switchcolumn`) = Summary, Focus, Experience, Projects. `paracol` is chosen specifically so the 2-page Master page-breaks cleanly across columns.
- **`letter`** ([cf-letter.tex](../engine/templates/styles/cf-letter.tex)) — different macro set (`\LetterDate`, `\Recipient`, `\Subject`, `\Greeting`, `\LetterBody`, `\Para`, `\Fill`, `\Signoff`, `\BuildLetter`). `\Fill` ([line 32](../engine/templates/styles/cf-letter.tex)) renders its argument in `\itshape\color{accent}` so the "[Why this company]" placeholder is visually unmissable. Wider margins (0.85in sides) and `\parskip=5pt` give it letter proportions.

All three accent-bearing styles default to `1F4E79`; `copy_styles()`/`copy_style()` rewrite that hex from `resume.accent_hex` at copy time, which is why the accent is set once in `config.yaml` and propagates to modern + twocol + letter while ats stays black.

---

**Next:** [05-ai-layer.md](05-ai-layer.md) (how the AI phases produce the `work/*.json` these renderers consume), then [06-data-contracts.md](06-data-contracts.md) (the exact JSON shapes) and [07-ci-and-extending.md](07-ci-and-extending.md) (running the gate in CI and adding a style/flavor).
