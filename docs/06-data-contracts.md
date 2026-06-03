# Data contracts reference

**Who/what:** the exact shapes the AI must emit and the engine consumes — `config.yaml` plus the four JSON knowledge files in `work/`, field-by-field, with required vs. optional and *what each field drives in the render*. 🔒 Proprietary, author-owned.

This is the authoritative spec for the boundary between the AI layer ([05-ai-layer.md](05-ai-layer.md)) and the deterministic engine ([04-engine.md](04-engine.md)). Each schema lives at [.github/skills/kaushal-forge/schemas/](../.github/skills/kaushal-forge/schemas/); the renders that read these fields live in [engine/](../engine/). For the phase pipeline that produces each file see [RUNBOOK.md](../RUNBOOK.md); for the overall data flow see [03-architecture.md](03-architecture.md).

The four `work/*.json` files are emitted by phases P1 (`profile.json`), P3 (`linkedin.json`), P4 (`variants.json`), P5 (`letters.json`). The schemas are JSON Schema 2020-12; the engine validates *behaviorally* — it `.get(...)`s fields and skips what is absent, so "optional" below means the renderer tolerates omission, not that the schema marks it optional. Fields the renderers never read are AI-only working context (called out explicitly).

---

## `config.yaml`

Copy [config.example.yaml](../config.example.yaml) to `config.yaml` and fill. Every renderer loads it via `yaml.safe_load`. Field-by-field:

| Path | Type | Required | Drives |
|---|---|---|---|
| `person.name` | str | yes | `\Name{}` on every résumé ([render_resumes.py:106](../engine/render_resumes.py)) and letter ([render_coverletters.py:58](../engine/render_coverletters.py)); signature line in `letter.md`. Read as `cfg["person"]["name"]` — KeyError if missing. |
| `person.pronouns` | str | optional | Author reference only; **not read by any renderer**. |
| `person.location_display` | str | optional | Appended to the résumé contact line verbatim. On letters only the part **before** the first `\|` is used (`loc.split("\|")[0]`, [render_coverletters.py:43](../engine/render_coverletters.py)). |
| `contact.email` | str | optional | `\href{mailto:...}` in résumé + letter contact lines. |
| `contact.phone` | str | optional | Contact line, escaped. |
| `contact.linkedin` | str | optional | `\href{https://...}`; scripts prepend `https://`, so store **without** scheme. Also echoed in the `letter.md` signature. |
| `contact.github` | str | optional | `\href{https://...}` in contact lines. |
| `contact.portfolio` | str | optional | Résumé contact line only ([render_resumes.py:52](../engine/render_resumes.py)); not in letters. Omit if none. |
| `targets.geos` | list[str] | optional | AI targeting context (P2); **not read by renderers**. |
| `targets.diplomatic` | bool | optional | AI tone/discoverability guidance; **not read by renderers**. |
| `resume.accent_hex` | str (6 hex, no `#`) | optional | Regex-injected into `\definecolor{accent}{HTML}{...}` of the modern/twocol résumé styles and the letter style. ATS style stays black. Default `""` = leave template's built-in color. |
| `resume.two_page` | `"all"` \| list[str] | optional | Which role-variant ids also get a `-2page` edition. `"all"` (default) = every variant; a list like `["05","06","07"]` restricts it. The 09 Master is always 2-page regardless. |
| `resume.cap_overrides` | map `id:int` | optional | Per-variant current-role bullet cap on the 1-pager. `int(cap_over.get(vid, 4))` — default cap is 4 ([render_resumes.py:171](../engine/render_resumes.py)). Use for dense variants whose 1-pager spills. |
| `verify.forbidden_terms` | list[str] | optional | Leak-scan terms (codenames, client/manager names). [verify.py](../engine/verify.py) fails the build if any (case-insensitive) appears in generated output. |

---

## `profile.json` — the structured knowledge base (P1)

Schema: [profile.schema.json](../.github/skills/kaushal-forge/schemas/profile.schema.json). An object. Drives the **09 Master** résumé and, everywhere, the shared education / certs / contact blocks. Required by schema: `identity, headline, summary, experience, education, skills_groups, achievements_bank`.

| Field | Type | Req | Drives |
|---|---|---|---|
| `identity.name` / `.pronouns` / `.location` | str | — | AI context. Renderers use `config.person.*` for identity, **not** this block. |
| `identity.tagline` | str | — | Fallback Master headline **only if** `headline` is empty ([render_resumes.py:155](../engine/render_resumes.py)). |
| `identity.handles` | obj | — | AI context; not rendered. |
| `headline` | str | yes | Master `\Headline{}`. |
| `summary` | str | yes | Master `\Summary{}` (2–4 lines). |
| `focus` | str | optional | Master `\FocusData{}`, emitted only when non-blank. |
| `experience[]` | array | yes | Master experience section. Each item needs `role, org, dates, location, bullets[]`. On the Master **all** bullets render (cap `None`). |
| `education[]` | array | yes | `\EduItem{degree}{institution}{dates}{detail}`. `detail` shows only in *full* (2-page / Master) editions; on 1-pagers it is blank ([render_resumes.py:60](../engine/render_resumes.py)). |
| `skills_groups[]` | array of `{label, items}` | yes | Master `\SkillRow{label}{items}`. `items` is a single comma-joined string, not an array. |
| `certs[]` | list[str] | optional | Extras block. Full edition lists all; 1-pager lists the **first 3** (`certs[:3]`, [render_resumes.py:76](../engine/render_resumes.py)). |
| `awards[]` | list[str] | optional | Full: all, joined by `;`. 1-pager: **first award only** (`awards[0]`). |
| `languages[]` | list[str] | optional | Extras line, comma-joined, both editions. |
| `projects[]` | array of `{name, meta, desc, url}` | optional | Master `\Project{name}{meta}{desc}`. `url` is **not** rendered. |
| `persona` | str | optional | **AI-only.** Authentic voice to preserve when drafting variants/letters. Never rendered. |
| `achievements_bank[]` | list[str] | yes (schema) | **AI-only.** The pool of quantified, leak-safe bullets the model draws from to build variants. Never rendered directly. |

> The Master is built straight from this file: only the `experience`, `skills_groups`, `projects`, education and extras blocks reach the page. `persona` and `achievements_bank` exist purely to give the model raw material for P3–P5.

---

## `variants.json` — tailored role résumés (P4)

Schema: [variants.schema.json](../.github/skills/kaushal-forge/schemas/variants.schema.json). A **top-level array** (the engine also tolerates `{"results":[...]}` / `{"variants":[...]}`). One object per role variant; drives `output/Resumes/<id>-<key>/`. Annotated example: [variant-content.example.json](../.github/skills/kaushal-forge/examples/variant-content.example.json). Required per item: `id, key, headline, summary, skills_rows, experience, guide_md`.

| Field | Type | Req | Drives |
|---|---|---|---|
| `id` | str | yes | Two-digit, e.g. `01`–`08`,`10`. **`09` is reserved** for the auto-built Master and is skipped if present. Names the output folder and sets `verify.py` page expectations. |
| `key` | str | yes | Kebab slug (e.g. `ai-genai-engineer`). Folder name = `<id>-<key>`. |
| `headline` | str | yes | `\Headline{}`. |
| `summary` | str | yes | `\Summary{}`. |
| `focus` | str | optional | `\FocusData{}`; `""` to omit. |
| `skills_rows[]` | array of `{label, items}` | yes | `\SkillRow{}`. The **1-pager keeps only the first 4 rows** (`skills_rows[:4]`); the 2-page edition keeps all. |
| `experience[]` | array `{role, org, dates, location, bullets[]}` | yes | Experience section. **1-pager bullet caps**: current role = `cap_overrides[id]` or 4, next two roles = 2, all further roles = 1 (`caps_1p = [cap0, 2, 2] + [1]*8`, [render_resumes.py:172](../engine/render_resumes.py)). 2-page edition = all bullets. |
| `projects[]` | array `{name, meta, desc}` | optional | `\Project{}`. **1-pager keeps the first 2** (`projects[:2]`); 2-page keeps all. Section omitted entirely when empty. (Note: variant projects have no `url`.) |
| `guide_md` | str | yes | Written verbatim to `GUIDE.md` in the variant folder (when to use, JD keywords, fit/odds, best style, tweak tips). The `-2page` folder gets an auto-generated stub GUIDE instead. |

Education, certs, awards, languages and contact on every variant come from `profile.json` + `config.yaml`, not from the variant object.

---

## `letters.json` — tailored cover letters (P5)

Schema: [letters.schema.json](../.github/skills/kaushal-forge/schemas/letters.schema.json). A **top-level array** (same `results`/`letters` tolerance). One object per letter; drives `output/CoverLetters/<id>-<key>/`. All string fields are HTML-entity-decoded before render (`deent`, [render_coverletters.py:90](../engine/render_coverletters.py)). Required: `id, key, email_subject, opening, body, closing, why_company_prompt, notes_md`.

| Field | Type | Req | Drives |
|---|---|---|---|
| `id` | str | yes | Folder = `<id>-<key>`. |
| `key` | str | yes | Folder slug (falls back to `id` if absent). |
| `email_subject` | str | yes | **`letter.md` only** — the `**Subject:**` line. Not in the PDF. |
| `opening` | str | yes | First `\Para{}` (the hook + `[Role] at [Company]`), in both `.tex` and `.md`. |
| `body[]` | list[str] | yes | One `\Para{}` per proof paragraph (1–2). |
| `closing` | str | yes | Final `\Para{}`, after the why-company fill. |
| `why_company_prompt` | str | yes | **`letter.md` only**, rendered as a `>` blockquote prompt. The `.tex` instead emits a fixed `\Fill{...}` placeholder the candidate replaces. |
| `notes_md` | str | yes | **`letter.md` only** — the "Notes (delete before sending)" section. |

Both files share the `[Date]`, `Hiring Team, [Company]`, `[Hiring Manager]`, and why-company placeholders, which the candidate fills before sending.

---

## `linkedin.json` — LinkedIn rewrite (P3)

Schema: [linkedin.schema.json](../.github/skills/kaushal-forge/schemas/linkedin.schema.json). An **object**; [render_linkedin.py](../engine/render_linkedin.py) is fully tolerant — it emits a section file only for the keys present. No top-level field is structurally required. Drives `output/LinkedIn/*.md`.

| Field | Type | Limit | Drives → file |
|---|---|---|---|
| `headline_variants[]` `{label, text}` | array | `text` ≤ 220 | `01-headline.md`; each option printed with a live char count. |
| `about.primary` | str | ≤ 2600 | `02-about.md`, "Primary". |
| `about.alt` | str | ≤ 2600 | `02-about.md`, "Shorter alt"; emitted only if present. |
| `experience[]` `{title, org, dates, location, bullets[], skills_line}` | array | ≤ 2000/role (advisory) | `03-experience.md`; `skills_line` appended as a `Skills:` line. |
| `skills.ordered[]` | list[str] | ≤ 50 | `04-skills.md`, "Keep, in priority order". |
| `skills.pin3[]` | list[str] | ≤ 3 | `04-skills.md`, "Pin these 3". |
| `featured[]` `{title, note}` | array | — | `05-featured-and-projects.md`. |
| `certs_order[]` | list[str] | — | `06-certs-education-awards.md`. |
| `misc[]` | list[str] | — | `07-misc-settings.md` (diplomatic discoverability tips). |

`00-overview.md` (apply order + a limits cheat-sheet) is always written, independent of input.

---

## `work/` file map

Source-of-truth knowledge files the AI maintains; renderers read from here. See [03-architecture.md](03-architecture.md) for the flow.

| Path | Phase | Schema | Consumed by |
|---|---|---|---|
| `work/profile.json` | P1 | profile | `render_resumes.py` (Master + shared blocks) |
| `work/targeting.json` | P2 | — | AI context for P3/P4 (no renderer) |
| `work/linkedin.json` | P3 | linkedin | `render_linkedin.py`, `verify.py` (limits) |
| `work/variants.json` | P4 | variants | `render_resumes.py` |
| `work/letters.json` | P5 | letters | `render_coverletters.py` |
| `work/strategy/*.md` | — | freeform md | `render_strategy.py` (copied verbatim) |

---

## `output/` tree

Produced by the renderers + [build_pdfs.py](../engine/build_pdfs.py); not committed. Page counts are enforced by [verify.py](../engine/verify.py).

```
output/
  Resumes/
    _styles/                      cf-ats.tex · cf-modern.tex · cf-twocol.tex   (accent injected)
    09-master-2page/              content.tex · build-{ats,modern,twocol}.tex · GUIDE.md   (2 pages)
    <id>-<key>/                   content.tex · build-{ats,modern,twocol}.tex · GUIDE.md   (1 page)
    <id>-<key>-2page/             content.tex · build-{ats,modern,twocol}.tex · GUIDE.md   (2 pages)
  CoverLetters/
    _styles/cf-letter.tex
    <id>-<key>/                   letter.tex · letter.md                                  (1 page)
  LinkedIn/
    00-overview.md … 07-misc-settings.md
  Strategy/
    00-index.md + copied work/strategy/*.md
```

Each résumé folder ships three `build-*.tex` drivers (ATS / modern / twocol) that all `\input{content.tex}` — one content file, three compiled looks.

### Limits `verify.py` enforces

| Check | Rule |
|---|---|
| Leak scan | No `config.verify.forbidden_terms` (case-insensitive) in `content.tex`, `letter.{tex,md}`, `LinkedIn/*.md`, `Strategy/*.md`. |
| HTML entities | None of `&gt; &lt; &amp; &#39; &quot;` may survive into output. |
| LinkedIn chars | headline `text` ≤ 220; `about.primary`/`about.alt` ≤ 2600 (read from `work/linkedin.json`). |
| PDF pages | role variants = 1; any `*-2page` folder or `09*` = 2; cover letters = 1. (Skipped with a note if `pypdf` is absent.) |

---

**Next:** [07-ci-and-extending.md](07-ci-and-extending.md) — how CI runs the verify gate and how to add a new flavor/field — or revisit [05-ai-layer.md](05-ai-layer.md) for how the model is prompted to fill these contracts.
