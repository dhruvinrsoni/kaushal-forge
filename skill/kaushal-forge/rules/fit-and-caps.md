# Fit & caps — how résumés stay 1-page / 2-page (the SCRIPT handles this)

You provide **full tailored content** per variant. `engine/render_resumes.py` decides what fits:

- **1-page edition** (role variants): auto-caps to skills = first 4 rows; experience bullets = current-role 4 (or `config.resume.cap_overrides[id]`, e.g. 3 for a dense variant), then 2 / 2 / 1; projects = first 2; education detail blank (kept for the research variant); compact one-line certs; class `extarticle` 9pt.
- **2-page edition** (ids in `config.resume.two_page`, default all): full content, all skills/bullets/projects, full education + certs, 10pt.
- **Master (id 09)**: built from `profile.json` directly (everything), 2-page.

So: **order content by importance** (most relevant skill group first; strongest bullet first in each role; best 2 projects first) — the caps keep the front, drop the tail. Don't pad; provide real, ranked content.

LaTeX styling, escaping, and the macro contract are entirely the script's job — you never write LaTeX. Three styles render from the same content: `ats` (plain, black, ATS-safe), `modern` (accent, single-column), `twocol` (sidebar). Accent colour comes from `config.resume.accent_hex`.
