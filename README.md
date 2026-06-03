# KaushalForge

> ✅ **Status: built & verified.** A full end-to-end dry-run on real data compiled **57 résumé PDFs + 10 cover-letter PDFs (67 total, 0 failures)** and passed `engine/verify.py` ("VERIFY OK"). `work/` and `output/` currently hold that **worked demo** (Dhruvin's data) — clear them (keep the `.gitkeep`) to start fresh for a new person; `config.yaml` is pre-filled, `config.example.yaml` is the blank template.
>
> 🔒 **Going public later:** `config.yaml`, `work/`, and `output/` are already gitignored (never tracked). The one thing to handle before flipping public is `.github/skills/kaushal-forge/examples/` — it ships **real sample data** as the gold-standard reference; anonymize it (or swap in a fictional sample) first.

A **repeatable, AI-powered career-toolkit generator.** Feed it a person's raw data; it produces a complete, tailored toolkit: a LinkedIn rewrite, multi-variant LaTeX résumés (compiled to PDF, 1- and 2-page), matching cover letters, and a strategy pack — reproducibly, **on any model** (Opus, Sonnet, or Haiku).

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
- `prompts/` — portable copy-paste prompt pack for non-Claude models.
- `config.yaml` · `inbox/` · `work/` · `output/`.

See `MASTER-PLAN.md` for the complete design.
