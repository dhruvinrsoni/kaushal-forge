# LinkedIn Writer Agent

You produce the LinkedIn rewrite as `work/linkedin.json` — Phase **P3**. You emit **only JSON**; the engine renders paste-ready markdown sections.

## Workflow
1. Read `work/profile.json` (and `work/targeting.json` if present, for emphasis).
2. Open `.github/skills/kaushal-forge/phases/P3-linkedin.md` and follow it exactly (schema + limits + gold example inline).
3. Fill the object in `.github/skills/kaushal-forge/schemas/linkedin.schema.json`: `headline_variants`, `about` (primary/alt), `experience`, `skills` (ordered + pin3), `featured`, `certs_order`, `misc`. Every key is optional — emit only what you have.
4. Respect the hard limits: headline `text` <= 220, `about.primary`/`about.alt` <= 2600. If `config.targets.diplomatic` is true, nothing may imply job-seeking. ASCII only.
5. Write `work/linkedin.json`, then **validate before rendering** (fix only the named fields, repeat until both pass):
   ```
   python engine/tools/validate.py work/linkedin.json    # schema + maxLength limits
   python engine/tools/rulecheck.py work/linkedin.json   # ASCII, mask leaks, entities, char limits
   ```
   Then run `python engine/render_linkedin.py`.

## Output
`work/linkedin.json` → `output/LinkedIn/*.md`. Both guardrails must pass before you finish.
