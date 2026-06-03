# RUNBOOK — operating KaushalForge end-to-end

Follow top to bottom. Each AI phase is a small, bounded "fill this schema like this example" task; each script is deterministic. Don't finish until `verify.py` exits 0.

## 0. Setup (once)
```
python engine/bootstrap.py            # installs pypdf + pyyaml; downloads/locates Tectonic
cp config.example.yaml config.yaml    # fill person/contact/targets/forbidden_terms
```

## 0b. Intake
- Put the person's raw data in `inbox/` (best LinkedIn source = their own **"Get a copy of your data"** export; plus performance reviews, an existing resume, GitHub README/portfolio text). Anything unreadable (odd PDFs), paste as `.txt`.
```
python engine/intake_dump.py          # -> work/00-raw-dump.txt
```

## 1–6. AI phases  (write JSON/MD to work/, then run the paired script)
| Phase | Read | Produce | Then run |
|---|---|---|---|
| P1 Structure | `work/00-raw-dump.txt` | `work/profile.json` | — |
| P2 Targeting | `work/profile.json` | `work/targeting.json` | — |
| P3 LinkedIn | profile | `work/linkedin.json` | `python engine/render_linkedin.py` |
| P4 Résumés | profile + targeting | `work/variants.json` | `python engine/render_resumes.py` |
| P5 Cover letters | variants | `work/letters.json` | `python engine/render_coverletters.py` |
| P6 Strategy | profile + targeting | `work/strategy/*.md` | `python engine/render_strategy.py` |

- **Claude Code:** invoke the `kaushal-forge` skill; it walks these phases. The phase prompts live in `skill/kaushal-forge/phases/PN-*.md` (schema + rules + gold example inline).
- **Any other model:** open `prompts/PN-*.md`, paste it + the needed `work/` file into the model, save the returned JSON to the path above. (`prompts/00-how-to-use.md` has the full loop.)

> Rule for the model: **emit only valid JSON / templated markdown** — never raw LaTeX, never prose outside the schema. The scripts do all rendering & escaping. Keep text ASCII.

## 7. Build & verify
```
python engine/build_pdfs.py           # compiles every résumé + letter; prints page counts
python engine/verify.py               # GATE: leaks, stray entities, char limits, page counts. Must print "VERIFY OK".
```
If `verify.py` fails, fix the flagged `work/*.json` field (or `config.forbidden_terms`) and re-run the paired render + build + verify.

## 8. Use the output
`output/Resumes/` (1- & 2-page × 3 styles), `output/CoverLetters/`, `output/LinkedIn/`, `output/Strategy/`.
Fill any `%FILL%` / `[bracket]` placeholders (email/phone in résumé `content.tex`; company/role in letters). Compile manually anytime: `tectonic <build-file>.tex` from inside the folder, or upload the folder to Overleaf.

## Refresh later (6 months on)
Update `inbox/`, re-run P1 (or hand-edit `work/*.json`), then re-render + build + verify. A cheap model handles every phase.
