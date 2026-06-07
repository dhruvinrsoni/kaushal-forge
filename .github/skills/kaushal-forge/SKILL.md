---
name: kaushal-forge
description: Generate a complete, tailored career toolkit (LinkedIn rewrite, multi-variant LaTeX résumés + PDFs, cover letters, and a strategy pack) from a person's raw data. Use when asked to build or refresh résumés, a LinkedIn profile, or a job-search toolkit from reviews / LinkedIn exports / GitHub. Works on any model — the AI only fills JSON schemas; scripts render & verify.
---

# kaushal-forge — orchestrator

You turn one person's raw data into a full career toolkit. **Your only job is to produce well-structured JSON / templated markdown.** All rendering (LaTeX → PDF), character counting, leak scanning, and page-count checking is done by deterministic scripts in `engine/`. Do not write LaTeX. Keep all text ASCII; the scripts handle escaping.

## Before you start
Confirm setup is done: `python engine/bootstrap.py` ran, `config.yaml` is filled, and `work/00-raw-dump.txt` exists (from `python engine/intake_dump.py`). If not, tell the operator to do that first.

## The loop (run phases in order; each writes one file to work/, then run its script)
| Phase | Open this prompt | Read | Write | Then run |
|---|---|---|---|---|
| P1 Structure | `phases/P1-structure.md` | `work/00-raw-dump.txt` | `work/profile.json` | — |
| P2 Targeting | `phases/P2-targeting.md` | `work/profile.json` | `work/targeting.json` | — |
| P3 LinkedIn | `phases/P3-linkedin.md` | profile (+targeting) | `work/linkedin.json` | `python engine/render_linkedin.py` |
| P4 Résumés | `phases/P4-resumes.md` | profile + targeting | `work/variants.json` | `python engine/render_resumes.py` |
| P5 Cover letters | `phases/P5-coverletters.md` | variants (+profile) | `work/letters.json` | `python engine/render_coverletters.py` |
| P6 Strategy | `phases/P6-strategy.md` | profile + targeting | `work/strategy/*.md` | `python engine/render_strategy.py` |

For each phase: open the phase file, follow it exactly (it contains the schema, the rules, and a gold example), write it to the named path, then **run the deterministic guardrails and fix any field they name before moving on**:
```
python engine/tools/validate.py    # work/*.json conforms to the schemas (exact field errors)
python engine/tools/rulecheck.py   # ASCII-only, no leaks/HTML-entities/GPA, LinkedIn limits
```
Then run the paired render script and confirm it printed `DONE`.

## Deterministic tools (your guardrails — `engine/tools/`)
The judge is a script, not your own judgement — so even a small/local model converges by fixing exactly what the tool reports. Loop: **write JSON -> validate -> rulecheck -> fix the named fields -> repeat until both pass.**
- `validate.py [files...]` — schema conformance (missing/extra/wrong-typed fields). Uses `jsonschema` if present, else a built-in shape check.
- `rulecheck.py [files...]` — content hygiene: non-ASCII, `config.verify.mask` leaks, HTML entities, GPA, LinkedIn char limits.
- `achievements.py <keywords>` — search `profile.achievements_bank` for real bullets to **select** when tailoring (never fabricate).
- `reword.py get|set <file> <id> <dotpath> [text]` — reword ONE field on request (e.g. `set variants 03 summary "..."`). Validates the new text (blocks a mask-leak/entity), writes it, and re-renders only that feed. Field-scoped so a small model can't drift the document. After a `set`, rebuild + verify.

**Working on a tiny/local model:** fill each `work/*.json` in **small passes** (P1: identity+summary → experience → rest → `achievements_bank`), run `validate.py`+`rulecheck.py` after each, and fix only the fields they name. The deterministic judge is what lets a weak model converge — see the per-phase files and `prompts/00-how-to-use.md`.

## Review checkpoint (after render, before you finish — STOP for the human)
Once `render_resumes.py` has written `content.tex`, run the review step and **pause for the operator**:
```
python engine/review.py         # -> work/review.yaml + work/REVIEW.md
```
Tell the operator to read `work/REVIEW.md` (schema status, page-2 fill, headlines, hygiene advisories), fix any `work/*.json`, and flip `approve: 0` on variants they don't want. Don't proceed to build the final set on their behalf without their go-ahead. Schema-clean variants default to `approve: 1`; the gate is non-interactive-friendly (no flag = build all), so CI is unaffected.

## Finish
```
python engine/build_pdfs.py     # compiles every résumé + letter (or --approved to build only approved ids)
python engine/verify.py         # GATE — must print "VERIFY OK"
```
**Do not consider the job done until `verify.py` exits 0.** If it fails, fix the flagged `work/*.json` field (or add the leaked term to `config.verify.mask` only if it's a false positive), then re-run the paired render + build + verify.

## Non-negotiable rules (full text in `rules/`)
- **Confidentiality/honesty** (`rules/confidentiality.md`): omit GPA; generalise client names to a category; strip internal codenames (keep the metrics); frame AI-assisted work as "AI-augmented engineering"; if `targets.diplomatic` is true, **nothing public may imply job-seeking**; **never fabricate** — every claim must trace to `work/00-raw-dump.txt`.
- **LinkedIn limits** (`rules/linkedin-limits.md`): Headline ≤220, About ≤2600, Experience ≤2000/role, ≤50 skills (pin 3), title ≤100.
- **Fit & caps** (`rules/fit-and-caps.md`): the scripts enforce 1-page vs 2-page automatically; you just provide full tailored content per variant.
- **Style/voice** (`rules/style-guide.md`): preserve the person's authentic voice; metrics over adjectives; STAR-ready bullets; ASCII only.

Gold-standard filled examples for every phase are in `examples/`.
