# MASTER PLAN — "KaushalForge": a repeatable, AI-powered Career-Toolkit Generator

> **What this plan is.** A single, self-contained, multi-phase build spec. When executed (by *any* model — Opus, Sonnet, or even Haiku) it produces ONE project folder that can regenerate the entire career toolkit we built this session — LinkedIn rewrite + tailored résumés (LaTeX→PDF) + cover letters + strategy docs — for **any person**, again and again, with **lower models**.
>
> **Why it can run on weak models.** The design splits work into two kinds: **(a) mechanical** (rendering LaTeX, compiling PDFs, counting characters, scanning for leaks, checking page counts) → handled by **deterministic Python scripts that need zero intelligence**; and **(b) judgement** (writing tailored content) → handled by the AI, but constrained to **fill rigid JSON schemas with worked examples beside them**, so a weaker model pattern-matches instead of inventing. A final verify-gate catches mistakes the model makes. This is the whole trick.
>
> **Provenance.** Everything here is the *generalization of artifacts we already built and proved this session* in `journey/` (the `_source/` generators, `Resumes/_styles/`, `LinkedIn/`, `Strategy/`, `CoverLetters/`). The executor mostly **copies + parameterizes proven files** per explicit instructions — not invents from scratch. Reference originals live in `journey/` and `journey/_source/`.

---

## CONTEXT — the need

We hand-built a complete career toolkit this session using Opus 4.8 + heavy effort + the user's own well-structured inputs (LinkedIn export, performance reviews). The user wants to **encapsulate that capability into one repeatable package** so that: (1) it survives losing access to top-tier models; (2) it can be re-run for maintenance (e.g., 6 months later) with a cheap model; (3) it can serve other people too. The output is **not another bespoke app** — it's an AI-guided pipeline: deterministic scripts for the definite parts + a master **Skill** (and portable prompts) for the AI-guidance parts + an intake step that ingests/cleans raw data.

**Intended outcome:** running this plan creates `journey/kaushal-forge/` — a self-documenting repo that, given a person's raw data in `inbox/` and a `config.yaml`, produces the full toolkit in `output/`, reproducibly, on any model.

---

## THE PRODUCT — `kaushal-forge/` (rename freely)

A repo with **three layers** + an **orchestrator** + **inputs/outputs**:

```
kaushal-forge/
├── MASTER-PLAN.md            # copy of THIS plan (seed/spec)
├── README.md                 # what it is + 60-second quickstart
├── RUNBOOK.md                # the step-by-step the operator/agent follows (the orchestrator)
├── config.example.yaml       # person config template (copy to config.yaml)
│
├── engine/                   # LAYER 1 — deterministic, model-agnostic Python (the "static/definite" works)
│   ├── bootstrap.py          # install Tectonic + pypdf + pyyaml if missing (Win/mac/Linux)
│   ├── intake_dump.py        # concatenate inbox/** -> work/00-raw-dump.txt (txt/md/csv + pdf text)
│   ├── render_resumes.py     # work/{profile,variants}.json + config -> Resumes/** (.tex, 1- & 2-page)
│   ├── render_coverletters.py# work/letters.json + config -> CoverLetters/**
│   ├── render_linkedin.py    # work/linkedin.json -> LinkedIn/*.md (paste-ready)
│   ├── render_strategy.py    # work/strategy/*.md passthrough -> output/Strategy/ (+ index)
│   ├── build_pdfs.py         # compile every build-*.tex / letter.tex; report pass/fail + page counts (--approved)
│   ├── verify.py             # char-limit + leak-scan + page-count + page-2-fill gate (exit !=0 on fail)
│   ├── review.py             # -> work/review.yaml + work/REVIEW.md (human approve checkpoint)
│   ├── run.py                # one-command orchestrator for the deterministic span (render->build->verify->review)
│   ├── publish.py            # selected résumés -> docs/ GitHub Pages hub (Full-Name-Resume-Role-Style.pdf)
│   ├── kf_lib.py             # shared paths/config/mask/limits (verify + tools import it)
│   ├── tools/                # deterministic guardrails: validate.py · rulecheck.py · achievements.py
│   └── templates/
│       └── styles/           # the 4 proven LaTeX styles (copied, de-personalised)
│           ├── cf-ats.tex  cf-modern.tex  cf-twocol.tex  cf-letter.tex
│
├── .github/skills/           # LAYER 2 — the AI "core engine" (Claude Code Skill format)
│   └── kaushal-forge/
│       ├── SKILL.md          # master orchestrator skill (frontmatter + the runbook the agent follows)
│       ├── phases/           # one self-contained prompt per judgement step (schema + rules + example inline)
│       │   ├── P1-structure.md  P2-targeting.md  P3-linkedin.md
│       │   ├── P4-resumes.md    P5-coverletters.md  P6-strategy.md
│       ├── schemas/          # the JSON contracts the scripts consume (profile/variants/letters/linkedin)
│       ├── rules/            # confidentiality.md · linkedin-limits.md · style-guide.md · fit-and-caps.md
│       └── examples/         # this session's outputs as filled references (gold standard)
│
├── prompts/                  # LAYER 3 — portable "any-model" pack (ChatGPT/Gemini/Sonnet/Haiku)
│   ├── 00-how-to-use.md      # paste-this-then-that workflow for a chat-only model
│   └── P1..P6 standalone prompts (system + instructions + schema + example, copy-paste ready)
│
├── inbox/   (.gitkeep)       # drop raw data here (LinkedIn export, reviews, csv, etc.)
├── work/    (.gitkeep)       # intermediate JSON/MD the AI produces & scripts consume
└── output/  (.gitkeep)       # final toolkit: LinkedIn/ Resumes/ CoverLetters/ Strategy/ 00-START-HERE.md
```

---

## THE PIPELINE (what a run does, end-to-end)

Inputs: `inbox/` (raw data) + `config.yaml`. Output: `output/` (full toolkit). Phases alternate **AI (fills JSON)** ↔ **script (renders/checks)**:

| # | Step | Who | In → Out |
|---|---|---|---|
| 0 | **Setup** | script | `bootstrap.py` installs Tectonic+pypdf+pyyaml |
| 0b | **Intake** | human+script | drop files in `inbox/`; `intake_dump.py` → `work/00-raw-dump.txt` |
| 1 | **Structure/clean** (data-mining) | AI (P1) | raw-dump → `work/profile.json` (+ `work/_source/*.md` KB) |
| 2 | **Targeting & counsel** | AI (P2) | profile → `work/targeting.json` (roles, counsel, variant list) |
| 3 | **LinkedIn content** | AI (P3) | profile → `work/linkedin.json` → `render_linkedin.py` → `output/LinkedIn/` |
| 4 | **Résumé content** | AI (P4) | profile+targeting → `work/variants.json` → `render_resumes.py` → `output/Resumes/` |
| 5 | **Cover-letter content** | AI (P5) | variants → `work/letters.json` → `render_coverletters.py` → `output/CoverLetters/` |
| 6 | **Strategy docs** | AI (P6) | profile+targeting → `work/strategy/*.md` → `render_strategy.py` → `output/Strategy/` |
| 7 | **Build & verify** | script | `build_pdfs.py` (all PDFs, page-checked) + `verify.py` (gate) |
| 8 | **Assemble** | script/AI | `00-START-HERE.md` index; report |

The AI only ever emits **structured JSON or templated markdown**; every render/compile/check is a script. Re-running any single phase is safe and idempotent.

---

## EXECUTION INSTRUCTIONS (for the future weak-model session — the actual build steps)

> Run these in order. Each is small and bounded. File contents to create are specified; for "harvest" steps, copy the named existing file and apply the listed edits. Prefer copying proven files over rewriting.

### STEP A — scaffold
1. Create `journey/kaushal-forge/` and the tree above (empty dirs get `.gitkeep`).
2. Copy this plan to `kaushal-forge/MASTER-PLAN.md`.
3. Write `README.md` (what it is + quickstart) and `RUNBOOK.md` (the operator runbook = a cleaned copy of the "THE PIPELINE" + "RUN IT" sections).

### STEP B — Layer 1 (engine) by harvesting the proven scripts
4. **`engine/templates/styles/`** ← copy the 4 style files verbatim, renamed:
   - `journey/Resumes/_styles/dhruvin-ats.tex` → `cf-ats.tex`
   - `…/dhruvin-modern.tex` → `cf-modern.tex`
   - `…/dhruvin-twocol.tex` → `cf-twocol.tex`
   - `journey/CoverLetters/_styles/dhruvin-letter.tex` → `cf-letter.tex`
   (They are already person-agnostic. Keep the compact spacing — it's tuned for 1-page/2-page fit.)
5. **`engine/render_resumes.py`** ← copy `journey/_source/_gen_resumes.py`, then generalize:
   - Replace the hardcoded `DATA_JSON` read with: load `config.yaml` (pyyaml) + `work/variants.json` + `work/profile.json`.
   - Move person constants to config / profile.json: `CONTACT` (build from `config.contact`), `EDU_*` and `EXTRAS*` (build from `profile.education` / `profile.certs`), `TWO_PAGE` (from `config.two_page` or default = all role ids), the `{"05":3}` cap override (from `config.cap_overrides`).
   - Keep verbatim: `esc()` (the escaping incl. HTML-entity decode, `->`→`$\rightarrow$`, `~`→`\textasciitilde{}`, smart quotes), the `\Name/\Headline/\Contact/\Summary/\FocusData/\SkillsData/\ExperienceData/\ProjectsData/\EducationData/\ExtrasData/\BuildResume` emission, the 1-page caps (skills[:4], bullets 4/2/2/1, projects[:2], extarticle 9pt) and 2-page full mode (article/extarticle 10pt) and `driver(style,pt)`.
   - Style path becomes `../../engine/templates/styles/cf-<style>.tex` (or copy styles next to output — see STEP F note).
6. **`engine/render_coverletters.py`** ← copy `journey/_source/_gen_coverletters.py`; same generalization (read `work/letters.json` + config; `\Recipient` uses `\newline` not `\\`; keep the `\Fill` short-placeholder + full prompt in `.md`).
7. **`engine/verify.py`** ← copy `journey/_source/_verify.py`; generalize the `FORBIDDEN` list to load from `config.verify.mask` (codenames/clients/manager+peer names per person); keep structure/escaping/char-count checks; **add** the page-count check (pypdf: role 1-pagers=1, master & *-2page=2, letters=1) and make the script **exit non-zero if any check fails** (so it's a real gate).
8. **`engine/build_pdfs.py`** ← new (small): find every `output/**/build-*.tex` and `output/**/letter.tex`, run Tectonic (`<tectonic> <file>` from the file's dir), collect exit codes + `pypdf` page counts, print a table + FAIL count. (Mirror the PowerShell loops we used; make it Python+subprocess for portability.)
9. **`engine/bootstrap.py`** ← new: detect/install Tectonic (download the GitHub release single binary to a local dir, as we did; cache path in a dotfile) and `pip install pypdf pyyaml`. Print the resolved tectonic path. Fallback message: "or use Overleaf."
10. **`engine/intake_dump.py`** ← new: walk `inbox/**`, read `.txt/.md/.csv` directly and extract text from `.pdf`/`.docx` (use pypdf / python-docx if available, else note which files need manual paste), concatenate into `work/00-raw-dump.txt` with `=== FILE: <name> ===` separators.
11. **`engine/render_linkedin.py`** & **`render_strategy.py`** ← new, simple: `render_linkedin.py` turns `work/linkedin.json` (keys: headline_variants[], about, experience[], skills, featured, certs, misc) into the 8 `output/LinkedIn/*.md` files using the section layouts from `journey/LinkedIn/*.md` as templates; `render_strategy.py` copies `work/strategy/*.md` to `output/Strategy/` and writes a small index.

### STEP C — Layer 2 (the Skill / AI core engine)
12. **`.github/skills/kaushal-forge/SKILL.md`** ← new. Frontmatter:
    ```
    ---
    name: kaushal-forge
    description: Generate a complete, tailored career toolkit (LinkedIn rewrite, multi-variant LaTeX résumés + PDFs, cover letters, strategy) from a person's raw data. Use when asked to build/refresh résumés, a LinkedIn profile, or a job-search toolkit from reviews/exports/GitHub.
    ---
    ```
    Body = the operator runbook: the phase table above + "for each phase, open phases/PN-*.md, follow it, write the JSON to work/, then run the named engine script; finally run build_pdfs.py and verify.py and do not finish until verify.py exits 0." Emphasise: **the model only writes JSON/MD; scripts render & check.**
13. **`.github/skills/kaushal-forge/rules/`** ← extract, verbatim where possible, from this session:
    - `confidentiality.md`: omit GPA; generalise client names → category (e.g., "Fortune-500 retail"); strip internal codenames; "AI-augmented engineering"; **no public job-seeking signal** (diplomacy); **no fabrication — every claim traces to the dump**. (Source: `journey/_source/master-profile.md` §9.)
    - `linkedin-limits.md`: Headline ≤220 · About ≤2600 · Experience desc ≤2000 each · ≤50 skills (pin 3) · title ≤100. (Source: `journey/LinkedIn/00-overview.md`.)
    - `fit-and-caps.md`: 1-page caps (skills 4 rows; bullets current 4 [dense→3], then 2/2/1; projects 2; 9pt extarticle) and 2-page full (10pt). LaTeX macro contract + `esc()` rules. (Source: the style files + `_gen_resumes.py`.)
    - `style-guide.md`: voice = preserve the person's authentic persona; metrics over adjectives; STAR-ready bullets; ASCII only in JSON (scripts escape).
14. **`.github/skills/kaushal-forge/schemas/`** ← the JSON contracts (these are the exact shapes that produced good output this session):
    - `profile.schema.json`: `{ identity{name,pronouns,location,tagline,handles{}}, contact{email,phone,linkedin,github,portfolio}, experience[{role,org,dates,location,bullets[]}], education[{degree,institution,dates,detail}], skills_groups[{label,items}], certs[], awards[], languages[], projects[{name,meta,desc,url}], persona, achievements_bank[] }`
    - `variants.schema.json` (per résumé variant): `{ id, key, headline, summary, focus, skills_rows[{label,items}], experience[{role,org,dates,location,bullets[]}], projects[{name,meta,desc}], guide_md }`
    - `letters.schema.json`: `{ id, key, email_subject, opening, body[], closing, why_company_prompt, notes_md }`
    - `linkedin.schema.json`: `{ headline_variants[], about, experience[{title,org,dates,bullets[]}], skills{ordered[],pin3[]}, featured[], certs_note, misc_settings }`
15. **`.github/skills/kaushal-forge/phases/PN-*.md`** ← one prompt each. Each MUST contain, inline: **(role)**, **(inputs/where to read)**, **(the schema)**, **(the relevant rules)**, **(a worked example from `examples/`)**, **(acceptance self-checks)**, **(output path in `work/`)**. Reuse the exact, proven instructions:
    - **P4-resumes.md** and **P5-coverletters.md**: paste the *agent prompts + schemas* we used in the two Workflow runs this session (resume-variants-draft and cover-letters-draft) — they are the gold instructions; just swap person-specific text for "read from `work/profile.json`."
    - **P1-structure.md**: instruct mining `work/00-raw-dump.txt` into `profile.json` per schema, applying `rules/confidentiality.md`; example = `journey/_source/master-profile.md` + `achievements-bank.md`.
    - **P2-targeting.md**: example = `journey/_source/role-targeting-and-counsel.md`. Output `targeting.json` (roles[], counsel, variant_list incl. a master + counsellor's-pick).
    - **P3-linkedin.md**: example = `journey/LinkedIn/*.md`. Output `linkedin.json`.
    - **P6-strategy.md**: example = `journey/Strategy/*.md` (career-strategy, global-visibility, masters, target-companies, interview-prep). Output `work/strategy/*.md`.
16. **`.github/skills/kaushal-forge/examples/`** ← copy this session's `_source/*.md`, a couple of `Resumes/*/content.tex`, `LinkedIn/02-about.md`, a `CoverLetters/*/letter.md`, and one `Strategy/*.md` as the gold-standard references the phase prompts point to.

### STEP D — Layer 3 (portable any-model pack)
17. **`prompts/`** ← for each phase, a standalone copy-paste prompt = the phase file's content reformatted for a chat-only model (system role + task + schema + example + "return ONLY valid JSON"). `00-how-to-use.md` explains: run setup+intake locally → paste P1 prompt + the dump into your model → save returned JSON to `work/profile.json` → run script → repeat P2..P6 → run build+verify. This is the **"works even without Claude/Opus"** guarantee.

### STEP E — config & docs
18. **`config.example.yaml`**:
    ```yaml
    person: { name: "", pronouns: "", location_display: "City, Country | Open to relocation" }
    contact: { email: "%FILL%", phone: "%FILL%", linkedin: "", github: "", portfolio: "" }
    targets: { geos: ["US","Canada","Australia","NZ"], diplomatic: true }   # diplomatic=true => no public job-seeking signal
    resume:
      accent_hex: "1F4E79"        # see output styles / PALETTE
      two_page: "all"             # or list of variant ids
      cap_overrides: { "05": 3 }   # current-role bullet caps for dense variants
    verify:
      forbidden_terms: []          # codenames, client names, manager/peer names to leak-scan for
    ```
19. Final `output/00-START-HERE.md` is generated by an assemble step (mirror `journey/00-START-HERE.md`).

### STEP F — note on style paths
The proven setup compiles each `build-*.tex` with `\input{../_styles/<style>.tex}`. Simplest robust choice for the generator: have `render_resumes.py`/`render_coverletters.py` **copy the relevant `cf-*.tex` into an `output/Resumes/_styles/` (and `output/CoverLetters/_styles/`)** and keep the `../_styles/` relative include. This preserves the exact, tested compile behaviour (Overleaf "upload folder" + local Tectonic both work).

---

## RUN IT (once built — the repeatable loop, ≤ the user's future ask)
```
python engine/bootstrap.py                 # one-time: install tectonic + deps
# drop raw data into inbox/ ; copy config.example.yaml -> config.yaml and fill
python engine/intake_dump.py               # -> work/00-raw-dump.txt
# --- AI phases (Claude Code: invoke the kaushal-forge skill; or use prompts/ with any model) ---
#   P1 -> work/profile.json   P2 -> work/targeting.json
#   P3 -> work/linkedin.json  P4 -> work/variants.json  P5 -> work/letters.json  P6 -> work/strategy/*.md
python engine/render_linkedin.py
python engine/render_resumes.py
python engine/render_coverletters.py
python engine/render_strategy.py
python engine/build_pdfs.py                 # compiles all PDFs, prints page-count table
python engine/verify.py                     # GATE: must exit 0 (char limits, leaks, pages, consistency)
```
Re-running 6 months later = update `inbox/`, re-run P1 (or hand-edit `work/*.json`), re-render. A weak model can do every AI phase because each is a bounded "fill this schema like this example" task, and `verify.py` catches slips.

---

## EMBEDDED REFERENCE (so this plan is self-sufficient even if `journey/` is gone)

**Confidentiality/honesty rules:** omit GPA; generalise client names to category; strip internal codenames (keep metrics); "AI-augmented engineering"; never signal job-seeking publicly (diplomatic mode); never fabricate — trace every claim to source.

**LinkedIn limits:** Headline 220 · About 2600 · Experience 2000/role · Skills 50 (pin 3) · Title 100.

**Résumé LaTeX macro contract** (style files implement these identically; `content.tex` is style-agnostic):
`\Name{} \Headline{} \Contact{} \Summary{} \FocusData{} \SkillsData{ \SkillRow{label}{items} … } \ExperienceData{ \Role{title}{org}{dates}{loc} \begin{Achvs}\Achv{…}\end{Achvs} … } \ProjectsData{ \Project{name}{meta}{desc} } \EducationData{ \EduItem{deg}{inst}{dates}{detail} } \ExtrasData{ \Cred{…} } \BuildResume`. Letters: `\Name \Contact \LetterDate \Recipient \Subject \Greeting \LetterBody{ \Para{…} \Fill{…} } \Signoff \BuildLetter`.

**`esc()` rules (Python, applied to all JSON text before LaTeX):** decode HTML entities (`&gt;`→`>` etc.); escape `& % # _ $`; `->`→`$\rightarrow$`; `~`→`\textasciitilde{}`; straight `"…"`→`` ``…'' ``. (Don't touch `--` dashes.)

**1-page caps:** skills 4 rows; bullets current-role 4 (dense variant →3), then 2/2/1; projects 2; class `extarticle` 9pt. **2-page:** full content; 10pt. **ATS style stays black; accent only in modern/twocol/letter.**

**Résumé variant schema:** `{id,key,headline,summary,focus,skills_rows[{label,items}],experience[{role,org,dates,location,bullets[]}],projects[{name,meta,desc}],guide_md}`.
**Cover-letter schema:** `{id,key,email_subject,opening,body[],closing,why_company_prompt,notes_md}`.

**Default variant set (role archetypes):** 01 Backend SWE · 02 Cloud/DevOps/SRE · 03 AI/GenAI · 04 AI Dev-Tools/Agentic · 05 Solutions/Cloud Architect · 06 Staff/Lead · 07 Research/ML Eng · 08 Forward-Deployed/MTS · 09 Master(2-page) · 10 Counsellor's-Pick. (P2 may adapt the set per person.)

---

## VERIFICATION (of the built generator — done at end of execution)
1. **Dry-run on this session's data:** copy `journey/_source/master-profile.md`→derive a `work/profile.json` (or hand-place the existing structured data), run P4/P5/P3/P6 → render → `build_pdfs.py` should produce PDFs and `verify.py` should exit 0. Compare against the known-good `journey/Resumes` & `journey/CoverLetters` outputs (same page counts, 0 leaks).
2. **Weak-model check:** confirm each `phases/PN-*.md` and `prompts/PN` is fully self-contained (schema + example + rules inline) so a Haiku-class model can complete it; confirm `verify.py` is a hard gate.
3. **Portability:** `bootstrap.py` resolves a working Tectonic; `build_pdfs.py` compiles all `build-*.tex`/`letter.tex`; page counts match (role 1p, master/2page 2p, letters 1p).
4. **Self-containment:** `kaushal-forge/` runs without reading anything outside itself (examples are copied in, not referenced by absolute path).

## Scope guardrails
- This plan **builds the generator**, not another bespoke toolkit. The person-specific toolkit is an *output* of running it.
- Keep the engine deterministic; keep AI confined to schema-filling. Resist adding a server/DB — static scripts + skill files + (optional) a GitHub Pages/Vercel static viewer for `output/` is the ceiling.
- Everything lives in the single `kaushal-forge/` folder.
