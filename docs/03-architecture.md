# Architecture & the pipeline

**Who/what:** for anyone forming a mental model of the whole system — the three layers, the orchestrator that drives them, the `inbox/ -> work/ -> output/` data flow, and the phase-by-phase pipeline that turns one person's raw data into a finished career toolkit.

> 🔒 Proprietary, author-owned. Internal documentation only.

KaushalForge is an **AI-guided pipeline**, not an app. It splits every task into two kinds of work: **mechanical** (render LaTeX, count characters, scan for leaks, count PDF pages) handled by deterministic Python that needs zero intelligence, and **judgement** (write tailored content) handled by an AI that is constrained to fill rigid JSON schemas. A final verify-gate catches the model's slips. That split is the whole design — see [MASTER-PLAN.md](../MASTER-PLAN.md) for the product rationale and [RUNBOOK.md](../RUNBOOK.md) for the operator loop. This doc is the structural map underneath both.

## The three layers + the orchestrator

The repo is three layers, an orchestrator that walks them, and three I/O directories.

| Layer | Path | What it is | Intelligence required |
|---|---|---|---|
| **Layer 1 — Engine** | [engine/](../engine/) | Deterministic, model-agnostic Python. Renders JSON/MD into LaTeX, compiles PDFs, runs the verify gate. | None |
| **Layer 2 — The Claude skill** | [.github/skills/kaushal-forge/](../.github/skills/kaushal-forge/) | A Claude Code Skill: an orchestrator [SKILL.md](../.github/skills/kaushal-forge/SKILL.md) plus self-contained phase prompts, JSON schemas, rules, and gold-standard examples. | The AI follows it |
| **Layer 3 — Portable prompts** | [prompts/](../prompts/) | The same phases reformatted as copy-paste prompts for any chat-only model (ChatGPT/Gemini/Sonnet/Haiku). | Any model |
| **Orchestrator** | [SKILL.md](../.github/skills/kaushal-forge/SKILL.md) / [RUNBOOK.md](../RUNBOOK.md) | The runbook that sequences the phases and the scripts. The skill *is* the orchestrator for Claude Code; the RUNBOOK is the same loop for a human operator. | — |

Layers 2 and 3 are two front-ends to the **same contract**: both emit identical JSON/MD into `work/`, and both hand off to the same Layer-1 scripts. Losing access to Claude does not break the pipeline — you switch from the skill to the `prompts/` pack and keep the same engine. That portability guarantee is why the model boundary is drawn where it is (below).

### The I/O directories

```
inbox/   raw input  — the person's data, dropped in as files (read-only to the pipeline)
work/    scratch    — intermediate JSON/MD: the AI writes here, scripts read here
output/  product    — the finished toolkit: LinkedIn/ Resumes/ CoverLetters/ Strategy/
```

`work/` is the seam between the two halves of the system. Everything to its left is judgement (AI); everything to its right is mechanical (scripts). The AI never touches `output/`, and the scripts never invent content — they only transform `work/` files plus `config.yaml`.

## Data flow

```
                 ┌──────────────────────────────────────────────────────────┐
                 │                       config.yaml                         │   cross-cutting contract
                 │  person · contact · resume(accent/two_page/caps) · verify  │   (read by every render + verify)
                 └──────────────────────────────────────────────────────────┘
                          │              │              │            │
   inbox/**               ▼              ▼              ▼            ▼
  (raw files)   ┌───────────────┐   render_*.py    render_*.py   verify.py
       │        │               │       │              │            │
       ▼        │               ▼       ▼              ▼            ▼
  intake_dump.py│   work/profile.json ─┐
       │        │   work/targeting.json│
       ▼        │   work/linkedin.json ─┼─► render_linkedin.py   ─► output/LinkedIn/
 work/00-raw-   │   work/variants.json ─┼─► render_resumes.py    ─► output/Resumes/
   dump.txt ───►│ AI work/letters.json ─┼─► render_coverletters.py► output/CoverLetters/
       (AI mines│   work/strategy/*.md ─┴─► render_strategy.py   ─► output/Strategy/
        the dump)        ▲                                            │
                         │                build_pdfs.py  ── Tectonic ─┤  (compiles build-*.tex / letter.tex)
                AI emits ONLY JSON/MD                                 ▼
                (no LaTeX, ASCII text)                            verify.py  ── GATE (exit 0 == done)
```

Read it left to right: raw files in `inbox/` get concatenated into a single dump, the AI mines that dump into structured `work/` files, the matching render script turns each `work/` file into an `output/` subtree, then `build_pdfs.py` compiles and `verify.py` gates. `config.yaml` feeds the render and verify steps but never the AI's judgement.

## The phase pipeline

Phases alternate **AI (fills a `work/` file)** then **script (renders/checks)**. Each AI phase is paired with exactly one render script that consumes its `work/` file and writes one `output/` subtree.

| # | Phase | Who | Reads | Writes | Paired render script → output |
|---|---|---|---|---|---|
| **P0** | Setup | script | — | `engine/.tectonic_path`, deps | [bootstrap.py](../engine/bootstrap.py) installs `pypdf` + `pyyaml`, resolves/downloads Tectonic |
| **P0b** | Intake | human + script | `inbox/**` | `work/00-raw-dump.txt` | [intake_dump.py](../engine/intake_dump.py) concatenates `.txt/.md/.csv/.json/.log/.tex` + extracted `.pdf`/`.docx` text with `=== FILE: <name> ===` separators |
| **P1** | Structure | AI | `work/00-raw-dump.txt` | `work/profile.json` | — (no render; profile is the shared KB) |
| **P2** | Targeting | AI | `work/profile.json` | `work/targeting.json` | — (roles, counsel, variant list) |
| **P3** | LinkedIn | AI | profile (+targeting) | `work/linkedin.json` | [render_linkedin.py](../engine/render_linkedin.py) → `output/LinkedIn/00..07-*.md` |
| **P4** | Résumés | AI | profile + targeting | `work/variants.json` | [render_resumes.py](../engine/render_resumes.py) → `output/Resumes/<id>-<key>/` |
| **P5** | Cover letters | AI | variants (+profile) | `work/letters.json` | [render_coverletters.py](../engine/render_coverletters.py) → `output/CoverLetters/<id>-<key>/` |
| **P6** | Strategy | AI | profile + targeting | `work/strategy/*.md` | [render_strategy.py](../engine/render_strategy.py) → `output/Strategy/` (+ `00-index.md`) |
| **P7** | Build & verify | script | `output/**` | PDFs, pass/fail | [build_pdfs.py](../engine/build_pdfs.py) then [verify.py](../engine/verify.py) (the gate) |

The AI phase prompts live at [.github/skills/kaushal-forge/phases/](../.github/skills/kaushal-forge/phases/) (P1–P6), each carrying its schema, rules, and a gold example inline; the portable equivalents are at [prompts/](../prompts/). The orchestrator table in [SKILL.md](../.github/skills/kaushal-forge/SKILL.md) is the canonical order. For the schema-by-schema contract see [06-data-contracts.md](06-data-contracts.md); for the AI-side prompting see [05-ai-layer.md](05-ai-layer.md); for what each script does internally see [04-engine.md](04-engine.md).

### What each render produces (code-accurate)

- **render_linkedin.py** is tolerant — it emits whatever sections are present in `linkedin.json` and stamps a live `len(...)` character count beside each headline/about block (limits are *enforced* later by `verify.py`, not here).
- **render_resumes.py** always renders `09-master-2page/` from `profile.json` (full content, `10pt`), then one folder per variant in `variants.json`. Each variant folder gets `content.tex`, three `build-*.tex` drivers (`ats`, `modern`, `twocol`), and `GUIDE.md`. The 1-page edition is capped (`[cap0, 2, 2] + [1]*8` bullets, `skills_rows[:4]`, `projects[:2]`, `9pt`); a `-2page` edition (full content, `10pt`) is also emitted for any id in `config.resume.two_page` (`"all"` ⇒ every role variant). Styles are copied into `output/Resumes/_styles/` with `config.resume.accent_hex` injected into the `\definecolor{accent}` line for `modern`/`twocol` (`ats` stays black).
- **render_coverletters.py** writes `letter.tex` (compilable, with `[bracketed]` fields to fill) and `letter.md` (the paste/edit version with notes) per letter, and copies `cf-letter.tex` with the same accent injection.
- **render_strategy.py** is a pure passthrough: it copies `work/strategy/*.md` to `output/Strategy/` and writes a generated `00-index.md`.

## Where the model boundary sits

The AI **only ever emits structured JSON or templated markdown** — never raw LaTeX, never prose outside a schema, and (per the skill's instruction) ASCII text only because the scripts own all escaping. This is enforced structurally, not by trust:

- The render scripts each carry their own `esc()` (see [render_resumes.py:29](../engine/render_resumes.py#L29)) that decodes HTML entities, escapes `& % # _ $`, maps `->` to `$\rightarrow$` and `~` to `\textasciitilde{}`, and converts straight quotes. The AI feeds plain text; the script makes it LaTeX-safe.
- LaTeX assembly (`\Name`, `\SkillRow`, `\Role`, `\Achv`, `\BuildResume`, etc.) lives entirely in the scripts. The model fills schema fields; it never writes a macro.
- This is why a weaker model works: every AI phase is a bounded "fill this schema like this example" task, and the worst a slip can do is produce a field that `verify.py` rejects.

## Idempotency and re-runnability

Every phase is safe to re-run, because each script reads `work/` + `config.yaml` and **overwrites** its `output/` subtree from scratch rather than appending:

- `intake_dump.py` rewrites `work/00-raw-dump.txt` wholesale on each run.
- The render scripts re-derive their `output/` folders from the current `work/` JSON, so re-running a single phase is the unit of iteration.
- `build_pdfs.py` recompiles every `build-*.tex`/`letter.tex` and exits non-zero on any compile failure; `verify.py` re-scans the whole `output/` tree.

The render scripts also tolerate input drift: `render_resumes.py` and `render_coverletters.py` accept either a bare list or a `{"results":[...]}` / `{"variants":[...]}` / `{"letters":[...]}` wrapper from the model. Hand-edited `content.tex`/`letter.tex` files survive until you deliberately re-run the render. **Refresh six months later** = update `inbox/`, re-run P1 (or hand-edit `work/*.json`), then re-render + build + verify — see [RUNBOOK.md](../RUNBOOK.md).

## config.yaml — the cross-cutting contract

[config.example.yaml](../config.example.yaml) (copied to `config.yaml`) is the one input read by the *mechanical* side of every phase, keeping person-specific constants out of both the AI's judgement and the scripts' code:

- **`person` / `contact`** → name, location, and the contact line on résumés and letters (`contact_line()` builds `mailto:`/`https://` links; scripts add the protocol).
- **`resume.accent_hex`** → injected into `modern`/`twocol`/letter styles (ATS stays black).
- **`resume.two_page`** → which variant ids also get a 2-page edition (`"all"` or a list).
- **`resume.cap_overrides`** → per-variant current-role bullet cap on the 1-pager (default 4).
- **`verify.forbidden_terms`** → the leak-scan list `verify.py` rejects across all output text (codenames, client names, manager/peer names).

For a worked persona, a filled `config.yaml` for **Asha Verma** (with `verify.forbidden_terms` listing internal codenames like *PromptForge* and *QuickLog*, and clients *Globex Systems* / *Initech Labs* generalised to a category) drives every render and is checked by the gate — the same data never appears verbatim in `output/`.

## The gate

A run is not done until `verify.py` exits 0. It performs four checks ([verify.py](../engine/verify.py)): (1) leak scan for `config.verify.forbidden_terms` across `content.tex`, `letter.tex/.md`, and all LinkedIn/Strategy markdown; (2) no stray HTML entities (`&gt;` etc.); (3) LinkedIn char limits read from `work/linkedin.json` (Headline ≤220, About ≤2600); (4) PDF page counts via `pypdf` (role folders = 1 page; `*-2page` and `09-*` = 2; letters = 1). Any failure prints the offending item and exits non-zero. Fix the flagged `work/*.json` field (or `config.verify.forbidden_terms` for a false positive) and re-run the paired render + build + verify.

**Next:** [04-engine.md](04-engine.md) for the deterministic scripts in depth, then [05-ai-layer.md](05-ai-layer.md) for the Claude skill and portable prompts, and [06-data-contracts.md](06-data-contracts.md) for the JSON schemas that bind them.
