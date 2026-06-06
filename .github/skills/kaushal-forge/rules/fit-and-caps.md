# Fit & caps — how résumés stay 1-page / 2-page (the SCRIPT handles this)

You provide **full tailored content** per variant. `engine/render_resumes.py` decides what fits:

- **1-page edition** (role variants): auto-caps to skills = first 4 rows; experience bullets = current-role 4 (or `config.resume.cap_overrides[id]`, e.g. 3 for a dense variant), then 2 / 2 / 1; projects = first 2; education detail blank (kept for the research variant); compact one-line certs; class `extarticle` 9pt.
- **2-page edition** (ids in `config.resume.two_page`, default all): full content, all skills/bullets/projects, full education + certs, 10pt.
- **Master (id 09)**: built from `profile.json` directly (everything), 2-page.

So: **order content by importance** (most relevant skill group first; strongest bullet first in each role; best 2 projects first) — the caps keep the front, drop the tail. Don't pad; provide real, ranked content.

LaTeX styling, escaping, and the macro contract are entirely the script's job — you never write LaTeX. Three styles render from the same content: `ats` (plain, black, ATS-safe), `modern` (accent, single-column), `twocol` (sidebar). Accent colour comes from `config.resume.accent_hex`.

## Page-2 fill (warn-only)

After build, `verify.py` measures how full **page 2** of each 2-page edition is and prints an advisory `FILL ...` note when it's below `config.resume.fill.target_min` (default 40%), recording every value in `output/fill-report.json`. It **never fails the build** and never auto-trims — it's a signal to a human, not a content instruction. A 40–70% page 2 reads as intentional; a near-empty one usually means the **1-page edition is the stronger artifact** for that role. **Never invent or pad bullets to fill page 2** — fabrication is a hard rule. The only levers are human judgement (ship the 1-pager) or genuinely adding real, ranked depth — never made-up content.
