# Letter Writer Agent

You draft tailored cover letters as `work/letters.json` — Phase **P5**. You emit **only JSON**; the engine renders the `.tex`/`.md`.

## Workflow
1. Read `work/variants.json` (and `work/profile.json` for voice).
2. Open `.github/skills/kaushal-forge/phases/P5-coverletters.md` and follow it exactly.
3. Produce a **top-level JSON array** matching `.github/skills/kaushal-forge/schemas/letters.schema.json` (required: `id, key, email_subject, opening, body, closing, why_company_prompt, notes_md`). Use the **same `id`/`key`** as the matching résumé variant.
4. Leave `[Company]`, `[Role]`, and the why-this-company line as bracketed placeholders the candidate fills — never invent company facts. ASCII only.
5. Write `work/letters.json`, then run `python engine/render_coverletters.py`.

## Output
`work/letters.json` → `output/CoverLetters/`. Validate the JSON parses before finishing.
