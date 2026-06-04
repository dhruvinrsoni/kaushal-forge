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

For each phase: open the phase file, follow it exactly (it contains the schema, the rules, and a gold example), validate your JSON parses, write it to the named path, run the paired script, and confirm it printed `DONE`.

## Finish
```
python engine/build_pdfs.py     # compiles every résumé + letter; prints page counts
python engine/verify.py         # GATE — must print "VERIFY OK"
```
**Do not consider the job done until `verify.py` exits 0.** If it fails, fix the flagged `work/*.json` field (or add the leaked term to `config.verify.mask` only if it's a false positive), then re-run the paired render + build + verify.

## Non-negotiable rules (full text in `rules/`)
- **Confidentiality/honesty** (`rules/confidentiality.md`): omit GPA; generalise client names to a category; strip internal codenames (keep the metrics); frame AI-assisted work as "AI-augmented engineering"; if `targets.diplomatic` is true, **nothing public may imply job-seeking**; **never fabricate** — every claim must trace to `work/00-raw-dump.txt`.
- **LinkedIn limits** (`rules/linkedin-limits.md`): Headline ≤220, About ≤2600, Experience ≤2000/role, ≤50 skills (pin 3), title ≤100.
- **Fit & caps** (`rules/fit-and-caps.md`): the scripts enforce 1-page vs 2-page automatically; you just provide full tailored content per variant.
- **Style/voice** (`rules/style-guide.md`): preserve the person's authentic voice; metrics over adjectives; STAR-ready bullets; ASCII only.

Gold-standard filled examples for every phase are in `examples/`.
