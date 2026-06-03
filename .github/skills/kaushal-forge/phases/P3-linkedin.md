# P3 — LinkedIn rewrite content

**Role:** Expert LinkedIn writer + recruiter. Max-utilise every section while staying diplomatic.

**Read:** `work/profile.json` (+ `work/targeting.json` for which roles to optimise keywords toward). **Write:** `work/linkedin.json`.

**Apply:** `rules/linkedin-limits.md` (Headline ≤220, About ≤2600, Experience ≤2000/role, 50 skills/pin3) and `rules/confidentiality.md` (esp. diplomacy: never "seeking/open/relocating/available" if `targets.diplomatic`).

**Produce `linkedin.json`** per `schemas/linkedin.schema.json`:
- `headline_variants`: 3–4 options, each ≤220, tuned to different target clusters; keep the person's signature phrase if they have one.
- `about.primary` (front-load the hook; metrics; one thesis) and `about.alt` (shorter).
- `experience[]`: each role = metric-led bullets + a `skills_line`.
- `skills`: `ordered` (≤50, most-searched first) + `pin3`.
- `featured`: lead with the person's strongest public/shipped work.
- `certs_order`, and `misc` (diplomacy/settings tips — e.g. recruiters-only Open-to-Work, turn off update-broadcasting).

**Gold examples:** `examples/linkedin-about.md` (+ the section shapes the renderer expects are in `engine/render_linkedin.py`).

**Then run:** `python engine/render_linkedin.py` → `output/LinkedIn/*.md`.

**Self-check:** JSON parses · every headline ≤220 · about ≤2600 · diplomatic tone · metrics not adjectives. (`verify.py` re-checks lengths.)
