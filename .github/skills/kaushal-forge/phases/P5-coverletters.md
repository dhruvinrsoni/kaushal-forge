# P5 — Cover-letter content (the proven cover-letter prompt)

**Role:** Expert cover-letter writer. One tailored letter per résumé variant.

**Read:** `work/variants.json` (the archetypes) + `work/profile.json` (achievements). **Write:** `work/letters.json` (a JSON array, one object per variant id incl. `09` as a general/all-purpose letter).

**Per letter, return** (`schemas/letters.schema.json`):
`{ id, key, email_subject, opening, body[], closing, why_company_prompt, notes_md }`

**Rules:**
- A cover letter is a **private document sent to a target employer** — so it MAY express genuine interest in the role and openness to relocation (the public-diplomacy rule does NOT apply here). Stay confident, specific, warm; never desperate or boastful.
- ~250–330 words across 3–4 short paragraphs. **Plain ASCII** (no LaTeX/markdown). Use bracket placeholders `[Company]`, `[Role]`, `[Hiring Manager]`, and a `[why-this-company]` hook.
- `opening`: a specific, non-generic hook tied to the archetype (NOT "I am writing to apply…").
- `body[]`: 1–2 paragraphs leading with the achievement most relevant to THIS archetype (exact numbers; trace to profile).
- `closing`: confident, friendly call to action.
- `why_company_prompt`: an instruction telling the candidate exactly what specific, researched detail to put in the `[why-this-company]` slot (one concrete detail beats generic praise).
- `notes_md`: when to use this letter · what to customize · tone.

**Letter archetypes:** same ids/keys as the résumé variants, plus `09 master-general` = a versatile all-purpose letter (for mixed/unknown roles). Mirror each résumé variant's emphasis in its letter.

**Gold example:** `examples/letter.example.md`.

**Then run:** `python engine/render_coverletters.py` → `output/CoverLetters/**` (letter.tex + letter.md per variant).

**Self-check:** JSON array parses · each has all keys · ASCII only · numbers exact · placeholders present · tone confident-not-desperate.
