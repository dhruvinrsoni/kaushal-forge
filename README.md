# KaushalForge

> 🔒 **Proprietary — All Rights Reserved** (see [LICENSE](LICENSE)). Personal data, generated output, and PDFs are **never committed** — only the résumés you explicitly choose get published. All examples are fully fictional ("Asha Verma / Acme Cloud").

**Turn one folder of a person's career history into a complete, tailored job-search toolkit** — a LinkedIn rewrite, multi-variant LaTeX résumés (PDF: 1- & 2-page × 3 styles), matching cover letters, and a strategy pack — reproducibly, **on any AI model** (Opus → Haiku). Then publish the résumés you pick to a GitHub Pages website.

It runs on cheap models because the work is split: the exact, boring parts (render LaTeX, compile PDFs, count characters, scan for leaks, check page counts) are **deterministic Python in `engine/`**; the judgement (writing tailored content) is the **AI, confined to filling rigid JSON schemas** with a worked example beside each. `engine/verify.py` is a hard gate that catches slips. Full tour in **[docs/](docs/README.md)**.

---

## Quick start

**Prerequisites:** Python 3.10+ and git. Tectonic (the LaTeX engine) installs itself.

### 1 · Put ALL the raw data in one folder
The person's LinkedIn *"Get a copy of your data"* export, performance reviews, an old résumé, GitHub/portfolio text — any mix of `.pdf .docx .txt .md .csv`. Keep it **outside the repo** (it's confidential).

### 2 · Set up (once)
```bash
python engine/bootstrap.py              # installs deps + Tectonic
cp config.example.yaml config.yaml      # fill name / contact / targets / verify.mask
```

### 3 · Ingest → write → build → verify
```bash
python engine/intake_dump.py --data /path/to/that/folder   # -> work/00-raw-dump.txt
```
Now the **AI phases (P1→P6)** turn that dump into structured JSON in `work/`. Pick one:
- **Claude Code** — invoke the **`kaushal-forge`** skill; it walks all six phases.
  Install it once: `ln -s "$PWD/.github/skills/kaushal-forge" ~/.claude/skills/kaushal-forge`
- **Any other model** (ChatGPT / Gemini / …) — paste the prompts from `prompts/`, one at a time. See [prompts/00-how-to-use.md](prompts/00-how-to-use.md).

Then render everything and run the gate — one block:
```bash
python engine/render_resumes.py
python engine/render_coverletters.py
python engine/render_linkedin.py
python engine/render_strategy.py
python engine/build_pdfs.py     # compiles every PDF, prints a page-count table
python engine/verify.py         # GATE — must print "VERIFY OK"
```

> **Automated, but yours to steer.** Every step is re-runnable and nothing is hidden: hand-edit any `work/*.json` or a generated `content.tex`, then re-run the step above. The AI only ever writes JSON/markdown — the scripts do all rendering, escaping, and checking.

---

## What you get — `output/` (gitignored)

| Folder | Contents |
|---|---|
| `output/Resumes/` | every role variant × {1-page, 2-page} × {ATS, modern, two-column} — `.tex` + `.pdf` + a `GUIDE.md` on when to use it |
| `output/CoverLetters/` | one tailored letter per variant (`.tex` PDF + paste-ready `.md`) |
| `output/LinkedIn/` | 8 paste-ready sections (headline, about, experience, skills, …) |
| `output/Strategy/` | career plan, target companies, interview prep, and more |

Fill any `[Company]` / `[Role]` / `%FILL%` placeholders before sending. Re-run any step anytime to refresh.

---

## Publish chosen résumés to the web

A polished static [GitHub Pages](https://pages.github.com/) hub — **grouped by role**, with **View / Download / Copy-link** on every résumé and a Copy-site-link button — listing **only the résumés you choose** (never cover letters, strategy, or raw data).

```bash
python engine/publish.py --scan    # 1. auto-catalog every generated résumé into publish.yaml (all 0)
#                                    2. edit publish.yaml: flip `publish: 1` on the ones to publish;
#                                       set `live: 1` to go public (labels/order optional)
python engine/publish.py           # 3. copies those PDFs into docs/resumes/ + rebuilds docs/index.html
git add publish.yaml docs && git commit -m "publish: update résumé hub" && git push
```

You only toggle `1`/`0` (or `true`/`false`) — `--scan` fills the list for you, and the hub groups a role's formats under one card (primary download + "Other formats"), so even several variants read as a curated portfolio rather than a buffet. The top-level **`live:` is a master switch** — set `live: 0` to take *everything* down at once (the hub reverts to the anonymized sample). Until you go live, the hub shows that sample.

### Going public + turning the website on (one time)
In the repo's **Settings**:
1. **Make the repository public.** (The proprietary LICENSE still applies — *source-available*, not open source.)
2. **Settings → Pages → Source → "GitHub Actions".**

Done. From then on **every push to `main` auto-deploys the hub** ([.github/workflows/pages.yml](.github/workflows/pages.yml)) to:

```
https://dhruvinrsoni.github.io/kaushal-forge/
```

**To reflect new or updated résumés:** re-run the two `publish.py` steps, commit `docs/`, and push — Pages redeploys in about a minute.

---

## Safety (please read)

- **Never put real data in a tracked file.** Feed it via `--data <folder>` or the gitignored `inbox/`; keep `config.yaml` local.
- Gitignored: `config.yaml`, `inbox/`, `work/`, `output/`, and **every common data format** (`*.pdf *.docx *.xlsx *.csv *.vcf …`). The **only** public artifacts are the résumés you flag in `publish.yaml` (→ `docs/resumes/`).
- `engine/verify.py` leak-scans `config.verify.mask` terms across outputs **and tracked source files**, and a **pre-commit hook** (installed by `bootstrap.py`) blocks staged leaks. Details in [SECURITY.md](SECURITY.md).

---

## More

| | |
|---|---|
| **Guided docs & deep dives** | [docs/](docs/README.md) |
| **Operator runbook (phase by phase)** | [RUNBOOK.md](RUNBOOK.md) |
| **Design & rationale** | [MASTER-PLAN.md](MASTER-PLAN.md) |
| **Contributing / security** | [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) |

## License

🔒 **Proprietary — All Rights Reserved.** See [LICENSE](LICENSE). KaushalForge is **not** open source: no use, reproduction, modification, or distribution without the author's prior written permission.
