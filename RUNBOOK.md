# RUNBOOK — operating KaushalForge end-to-end

Follow top to bottom. Each AI phase is a small, bounded "fill this schema like this example" task; each script is deterministic. Don't finish until `verify.py` exits 0.

## 0. Setup (once)
```
python engine/bootstrap.py            # installs pypdf + pyyaml; downloads/locates Tectonic
cp config.example.yaml config.yaml    # fill person/contact/targets/verify.mask
```

## 0b. Intake
- Put the person's raw data in `inbox/` (best LinkedIn source = their own **"Get a copy of your data"** export; plus performance reviews, an existing resume, GitHub README/portfolio text). Anything unreadable (odd PDFs), paste as `.txt`.
- **Keep confidential data out of the repo.** Instead of copying into `inbox/`, point intake at an external folder with `--data`:
```
python engine/intake_dump.py                       # -> work/00-raw-dump.txt  (reads inbox/)
python engine/intake_dump.py --data ~/career-data  # or ingest an out-of-tree folder
```
> **Never commit real data.** `config.yaml`, `inbox/`, `work/`, `output/`, and `*.pdf` are gitignored. The only thing ever made public is the résumés you select in `publish.yaml` (rendered into `docs/resumes/` by `engine/publish.py`) — never cover letters, strategy docs, the knowledge base, or raw inputs.

## 1–6. AI phases  (write JSON/MD to work/, then run the paired script)
| Phase | Read | Produce | Then run |
|---|---|---|---|
| P1 Structure | `work/00-raw-dump.txt` | `work/profile.json` | — |
| P2 Targeting | `work/profile.json` | `work/targeting.json` | — |
| P3 LinkedIn | profile | `work/linkedin.json` | `python engine/render_linkedin.py` |
| P4 Résumés | profile + targeting | `work/variants.json` | `python engine/render_resumes.py` |
| P5 Cover letters | variants | `work/letters.json` | `python engine/render_coverletters.py` |
| P6 Strategy | profile + targeting | `work/strategy/*.md` | `python engine/render_strategy.py` |

- **Claude Code:** invoke the `kaushal-forge` skill; it walks these phases. The phase prompts live in `.github/skills/kaushal-forge/phases/PN-*.md` (schema + rules + gold example inline).
- **Any other model:** open `prompts/PN-*.md`, paste it + the needed `work/` file into the model, save the returned JSON to the path above. (`prompts/00-how-to-use.md` has the full loop.)

> Rule for the model: **emit only valid JSON / templated markdown** — never raw LaTeX, never prose outside the schema. The scripts do all rendering & escaping. Keep text ASCII.

## 6.5 Review (human checkpoint — recommended)
```
python engine/review.py               # -> work/review.yaml + work/REVIEW.md
```
Open **work/REVIEW.md**: it lists every variant with schema status, page-2 fill, and headline, and flags hygiene advisories. Fix any `work/*.json`, then flip `approve: 0` in `work/review.yaml` on variants you don't want. Schema-clean variants default to `approve: 1`; re-running `review.py` keeps your flips. This never blocks — skip it to build everything.

## 7. Build & verify
```
python engine/build_pdfs.py           # compiles every résumé + letter; prints page counts
#   ...or build only what you approved in step 6.5:
python engine/build_pdfs.py --approved
python engine/verify.py               # GATE: leaks, stray entities, char limits, page counts. Must print "VERIFY OK".
```
If `verify.py` fails, fix the flagged `work/*.json` field (or `config.verify.mask`) and re-run the paired render + build + verify.

## 8. Use the output
`output/Resumes/` (1- & 2-page × 3 styles), `output/CoverLetters/`, `output/LinkedIn/`, `output/Strategy/`.
Fill any `%FILL%` / `[bracket]` placeholders (email/phone in résumé `content.tex`; company/role in letters). Compile manually anytime: `tectonic <build-file>.tex` from inside the folder, or upload the folder to Overleaf.

## Refresh later (6 months on)
Update `inbox/`, re-run P1 (or hand-edit `work/*.json`), then re-render + build + verify. A cheap model handles every phase.
