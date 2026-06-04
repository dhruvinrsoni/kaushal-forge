# KaushalForge

> ✅ **Status: built & verified.** A full end-to-end dry-run compiled **57 résumé PDFs + 10 cover-letter PDFs (67 total, 0 failures)** and passed `engine/verify.py` ("VERIFY OK"). To start a run, copy `config.example.yaml` → `config.yaml`, drop the person's data in `inbox/`, and follow the quickstart below. `config.yaml`, `inbox/`, `work/`, and `output/` are never tracked — clear them (keep the `.gitkeep`) to start fresh.
>
> 🔒 **Proprietary & private.** All-Rights-Reserved (see `LICENSE`); personal data, generated output, and PDFs are gitignored and never committed. The gold examples in `.github/skills/kaushal-forge/examples/` and the CI fixtures in `tests/fixtures/` are **fully fictional** ("Asha Verma / Acme Cloud") — safe to share. CI (`.github/workflows/ci.yml`) runs a render-smoke over the fixtures plus the `verify.py` gate on every push.
>
> 🔐 **Data safety.** Never put a real person's data in a tracked file. Feed raw data via `python engine/intake_dump.py --data <external/path>` (or the gitignored `inbox/`) and keep `config.yaml` local. The **only** public surface is the résumés you list in `publish.yaml` (copied to `docs/resumes/` by `engine/publish.py`) — cover letters, strategy docs, the knowledge base, and raw inputs are never published.

A **repeatable, AI-powered career-toolkit generator.** Feed it a person's raw data; it produces a complete, tailored toolkit: a LinkedIn rewrite, multi-variant LaTeX résumés (compiled to PDF, 1- and 2-page), matching cover letters, and a strategy pack — reproducibly, **on any model** (Opus, Sonnet, or Haiku).

## Documentation
New here? **[docs/](docs/README.md)** is a guided, top-to-bottom walkthrough — from a 15-minute local run to a line-by-line engine reading:
- **[Onboarding](docs/01-onboarding.md)** — get a green pipeline locally, fast.
- **[Concepts](docs/02-concepts.md)** · **[Architecture](docs/03-architecture.md)** — why it works and how it's shaped.
- **[Engine internals](docs/04-engine.md)** · **[AI layer](docs/05-ai-layer.md)** · **[Data contracts](docs/06-data-contracts.md)** — code-level depth.
- **[CI & extending](docs/07-ci-and-extending.md)** — testing and adding styles / phases / variants.

Operators can also jump to the step-by-step [RUNBOOK.md](RUNBOOK.md); the full design rationale lives in [MASTER-PLAN.md](MASTER-PLAN.md).

## Why it works on cheap models
Two kinds of work are split cleanly:
- **Mechanical** (render LaTeX, compile PDFs, count characters, scan for leaks, check page counts) → **deterministic Python in `engine/`**. Zero intelligence required; identical on any machine.
- **Judgement** (write tailored content) → the AI, but **confined to filling rigid JSON schemas** with a worked example beside each (`.github/skills/kaushal-forge/` or `prompts/`). A weak model pattern-matches instead of inventing, and **`engine/verify.py` is a hard gate** that catches slips.

So the quality floor is high even with a small model.

## 60-second quickstart
```bash
python engine/bootstrap.py                 # install deps + LaTeX engine (Tectonic)
cp config.example.yaml config.yaml         # fill in name/contact/targets
# put the person's data in inbox/  (LinkedIn "Get a copy of your data" export, reviews, resume, GitHub text…)
python engine/intake_dump.py               # -> work/00-raw-dump.txt
```
Then run the **AI phases** (each writes one JSON/MD file to `work/`):
- **In Claude Code:** invoke the **`kaushal-forge`** skill (see `.github/skills/kaushal-forge/SKILL.md`) — it orchestrates P1→P6. To make it loadable, **symlink or copy `.github/skills/kaushal-forge/` into `~/.claude/skills/`** (or a project-level `.claude/skills/`).
- **In any other model (ChatGPT/Gemini/Sonnet/Haiku):** use the copy-paste prompts in `prompts/` (see `prompts/00-how-to-use.md`).

Finally, render + build + verify:
```bash
python engine/render_linkedin.py
python engine/render_resumes.py
python engine/render_coverletters.py
python engine/render_strategy.py
python engine/build_pdfs.py                # compiles every PDF, prints page-count table
python engine/verify.py                    # GATE — must exit 0
```
Output lands in `output/` (LinkedIn / Resumes / CoverLetters / Strategy). Re-run anytime to refresh.

## Layout
- `MASTER-PLAN.md` — the full spec/rationale (how & why it's built).
- `RUNBOOK.md` — the operator's step-by-step.
- `engine/` — deterministic scripts + the 4 LaTeX styles.
- `.github/skills/kaushal-forge/` — the AI orchestrator skill (phases + schemas + rules + gold examples).
- `.github/` — CI (`workflows/ci.yml` render-smoke + security scan), issue/PR templates, and the shared `repo-maintenance` / `systematic-debugging` / `testing` skills.
- `prompts/` — portable copy-paste prompt pack for non-Claude models.
- `tests/fixtures/` — fully fictional sample run that the CI render-smoke exercises end to end.
- `CLAUDE.md` · `pyproject.toml` · `Makefile` — project context + Python tooling.
- `config.yaml` · `inbox/` · `work/` · `output/` — runtime I/O (gitignored).

See `MASTER-PLAN.md` for the complete design.

## License

🔒 **Proprietary — All Rights Reserved.** See [`LICENSE`](LICENSE). KaushalForge is **not** open source: no use, reproduction, modification, or distribution is permitted without the author's prior written permission.
