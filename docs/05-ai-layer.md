# The AI layer — skill, phases, prompts

**Who/what:** the "judgement half" of KaushalForge — the model-driven steps that read a person's data and emit structured JSON / markdown, which the deterministic [engine/](../engine/) then renders and gates. If [04-engine.md](04-engine.md) is the hands, this is the brain. Read that first if you want the render/verify mechanics; this doc is about what the model is *told* to do and *forbidden* from doing.

🔒 Proprietary, author-owned. Examples here use only the repo's fictional persona (Asha Verma / Acme Cloud Technologies / Globex Systems / Initech Labs).

> ⚠️ **AI-assisted output.** The model only drafts; a human must review and own every claim. Outputs carry an AI-assisted disclaimer (operator drafts: `GUIDE.md`, LinkedIn overview, Strategy index, the cover-letter `.md` notes), and the engine gates the approved build + publish on a `reviewed: 1` sign-off. The résumé/letter PDFs themselves stay clean (no stamp).

---

## The hard line: the model only fills schemas

The single most important constraint, stated at the top of the skill ([SKILL.md](../.github/skills/kaushal-forge/SKILL.md):8):

> **Your only job is to produce well-structured JSON / templated markdown.** All rendering (LaTeX → PDF), character counting, leak scanning, and page-count checking is done by deterministic scripts in `engine/`. Do not write LaTeX. Keep all text ASCII; the scripts handle escaping.

Concretely, the model is constrained to:

- **Emit ONLY JSON** for P1–P5 (P6 emits plain markdown files). Every phase prompt repeats "Return ONLY valid JSON" and ends with a "JSON parses" self-check.
- **Never write LaTeX.** Content is plain structured text; the render scripts own the macro contract, styling, and escaping ([rules/fit-and-caps.md](../.github/skills/kaushal-forge/rules/fit-and-caps.md):11).
- **ASCII only.** The model writes `$0`, `~80x`, `10-15%`, `->` and the scripts convert/escape them — `->` to an arrow, `~` to a tilde, smart-quotes, and HTML/LaTeX-unsafe characters ([rules/style-guide.md](../.github/skills/kaushal-forge/rules/style-guide.md):7).

That last point is not just convention — it is *enforced*. [engine/verify.py](../engine/verify.py) scans every rendered output for stray HTML entities (`&gt;`, `&lt;`, `&amp;`, `&#39;`, `&quot;`) and hard-fails if any appear ([verify.py](../engine/verify.py):23,35). So if the model had emitted raw `>` and the script had failed to escape it, the gate catches it. The division of labour is structural, not trusted.

---

## The orchestration loop (SKILL.md)

[SKILL.md](../.github/skills/kaushal-forge/SKILL.md) is the orchestrator. After confirming setup (`bootstrap.py` ran, `config.yaml` filled, `work/00-raw-dump.txt` exists), it runs six phases **in strict order**, each producing exactly one artifact in `work/` and then running its paired engine script:

| Phase | Reads | Writes | Then runs |
|---|---|---|---|
| **P1** Structure | `work/00-raw-dump.txt` | `work/profile.json` | — |
| **P2** Targeting | `work/profile.json` | `work/targeting.json` | — |
| **P3** LinkedIn | profile (+targeting) | `work/linkedin.json` | `render_linkedin.py` |
| **P4** Résumés | profile + targeting | `work/variants.json` | `render_resumes.py` |
| **P5** Cover letters | variants (+profile) | `work/letters.json` | `render_coverletters.py` |
| **P6** Strategy | profile + targeting | `work/strategy/*.md` | `render_strategy.py` |

For each phase the loop is identical: open the phase file, follow it exactly, write it to the named path, **run the deterministic guardrails and fix exactly what they name**, then run the paired script and confirm it printed `DONE`.

### The validate-and-retry loop (why it works on weak models)

After writing each `work/*.json`, the phase runs:

```
python engine/tools/validate.py    # schema conformance — exact offending field path
python engine/tools/rulecheck.py   # ASCII, no mask-leaks/entities/GPA, LinkedIn limits
```

The **judge is a script, not the model's own judgement.** A weak/local model doesn't have to be reliably correct in one shot — it writes JSON, reads the precise field errors ("`0/skills_rows` is not of type array"), and fixes only those, repeating until both tools pass. Determinism upstream is what lets the whole pipeline run on cheap models. (`verify.py` runs `validate.py` again as a pre-check, so a malformed `work/*.json` surfaces as a `SCHEMA ...` failure even if a phase skipped the loop.) See [07-ci-and-extending.md](07-ci-and-extending.md#the-bundled-tools-enginetools).

**Small passes for tiny models.** P1 and P2 explicitly tell the model to fill the file in fragments (P1: identity+summary → experience → the rest → `achievements_bank`) and validate after each, rather than emitting the whole document at once. A ~1B local model pattern-matches a small fragment against the inline example far more reliably than a 200-line file. The same micro-step + paste-the-error-back guidance is mirrored into `prompts/00-how-to-use.md` for non-Claude models.

**Conversational reword (`engine/tools/reword.py`).** To change one field on request, the model proposes new text for just that field and `reword.py set <file> <id> <dotpath> "..."` applies it: it validates the *new text* (blocking a mask-leak or HTML entity, warning on non-ASCII), writes it back, and re-renders only that feed. Because the edit is field-scoped, a small model can't drift the rest of the document — the user keeps full control, one field at a time.

### The gate: "don't finish until verify.py exits 0"

The finish step is non-negotiable ([SKILL.md](../.github/skills/kaushal-forge/SKILL.md):26-30):

```
python engine/build_pdfs.py     # compiles every résumé + letter; prints page counts
python engine/verify.py         # GATE — must print "VERIFY OK"
```

> **Do not consider the job done until `verify.py` exits 0.**

When it fails, the instruction is to fix the flagged `work/*.json` field (or, only for a genuine false positive, add the term to `config.verify.mask`), then re-run the paired render + build + verify. The gate checks four things: forbidden-term leaks, stray HTML entities, LinkedIn char limits read straight from `work/linkedin.json` (headline > 220, about > 2600 → fail, at [verify.py](../engine/verify.py):42,45), and PDF page counts. See [04-engine.md](04-engine.md) for the full gate mechanics.

---

## Each phase is self-contained

A deliberate design choice for **model-agnosticism**: every `phases/PN-*.md` file inlines its **schema + rules + a gold example**, so a weak model can pattern-match without holding the whole repo in context. You hand it one phase, it produces one file.

### P1 — Structure ([phases/P1-structure.md](../.github/skills/kaushal-forge/phases/P1-structure.md))
**Role:** meticulous career analyst. **Reads** `work/00-raw-dump.txt`, **writes** `work/profile.json`. It extracts canonical identity / experience (exact titles, orgs, dates) / education / skills / certs / projects / persona, and — critically — builds an **`achievements_bank`**: every quantified, codename-free, client-safe bullet, which is the raw material P4 and P5 later *select* from. It also writes a master headline + summary, and lists back to the operator any codenames / client names / manager names it stripped, so they can be added to `config.verify.mask`. Schema: [schemas/profile.schema.json](../.github/skills/kaushal-forge/schemas/profile.schema.json) (see [06-data-contracts.md](06-data-contracts.md) for the field-level contract).

### P2 — Targeting ([phases/P2-targeting.md](../.github/skills/kaushal-forge/phases/P2-targeting.md))
**Role:** a mentor who knows the real market. **Reads** `profile.json`, **writes** `work/targeting.json`: an honest read of the person's history, a set of recommended role archetypes each with `odds` (High/Medium/Stretch), a single high-conviction `counsel` bet, and a `variant_list` of stable ids the downstream scripts key on. It works off a default archetype set (`01` backend SWE through `08` forward-deployed, `09` auto-built Master, `10` counsellor's-pick) but is told to adapt them to the actual person. The instruction is honest calibration, not flattery — name real PhD/credential/brand gaps and how to dissolve them.

### P3 — LinkedIn ([phases/P3-linkedin.md](../.github/skills/kaushal-forge/phases/P3-linkedin.md))
**Role:** expert LinkedIn writer + recruiter. **Reads** profile (+targeting), **writes** `work/linkedin.json` per [schemas/linkedin.schema.json](../.github/skills/kaushal-forge/schemas/linkedin.schema.json): 3–4 headline variants (each ≤220), an `about.primary` + shorter `about.alt`, per-role experience with a `skills_line`, an ordered ≤50 skills list with 3 pinned, featured work, and diplomacy/settings tips. Then runs `render_linkedin.py` → `output/LinkedIn/*.md`. Applies the LinkedIn-limits and confidentiality rules below.

### P4 — Résumés ([phases/P4-resumes.md](../.github/skills/kaushal-forge/phases/P4-resumes.md))
**Role:** expert technical résumé writer. **Reads** profile + targeting, **writes** `work/variants.json` — a JSON *array*, one object per variant id in `variant_list` (excluding `09`, the auto-built Master). Each object carries headline / summary / focus / `skills_rows` / `experience` / `projects` / `guide_md` per [schemas/variants.schema.json](../.github/skills/kaushal-forge/schemas/variants.schema.json). The key discipline: **tailor by selection, ordering, and light rephrasing of `achievements_bank` — never invention**, with exact titles/dates from the profile. The model orders content by importance because the script auto-caps the 1-page edition; it does not decide page fit. Then runs `render_resumes.py` → `output/Resumes/**`.

### P5 — Cover letters ([phases/P5-coverletters.md](../.github/skills/kaushal-forge/phases/P5-coverletters.md))
**Role:** expert cover-letter writer. **Reads** `variants.json` + profile, **writes** `work/letters.json` (array, one per variant id *including* `09` as a general all-purpose letter) per [schemas/letters.schema.json](../.github/skills/kaushal-forge/schemas/letters.schema.json). Each letter is ~250–330 words, ASCII, with bracket placeholders (`[Company]`, `[Role]`, `[Hiring Manager]`, `[why-this-company]`). Note the deliberate carve-out: a cover letter is a **private** document sent to a target employer, so it MAY express interest in the role and openness to relocation — the public-diplomacy rule does *not* apply here. Then runs `render_coverletters.py`.

### P6 — Strategy ([phases/P6-strategy.md](../.github/skills/kaushal-forge/phases/P6-strategy.md))
**Role:** career mentor. **Reads** profile + targeting, **writes** plain markdown files into `work/strategy/` (career-strategy, global-visibility-playbook, online-masters-bridge, in-person-masters-usa, target-companies, interview-prep — adapted to the person). The hard rules: STAR stories must cite the person's *real, traceable* metrics from `achievements_bank`, and any comp/visa claim must be framed as directional with a "verify / consult an immigration attorney" caveat — never invented. Then runs `render_strategy.py` → `output/Strategy/`.

---

## The four rules files

Inlined into the phase prompts and stated in full under [rules/](../.github/skills/kaushal-forge/rules/). They apply across phases:

- **Confidentiality & honesty** ([rules/confidentiality.md](../.github/skills/kaushal-forge/rules/confidentiality.md)) — omit GPA on experienced résumés; generalise client names to a category (e.g. real clients → "Fortune-500 retail & pharmacy clients"); strip internal codenames but **keep the metrics**; frame AI-assisted work as "AI-augmented engineering"; if `config.targets.diplomatic` is true, nothing *public* may imply job-seeking / leaving / relocating-out; and the bedrock rule — **no fabrication**, every claim/metric/title/date must trace to `work/00-raw-dump.txt`. It also instructs adding stripped codenames and names to `config.verify.mask` so `verify.py` hard-fails on any leak.
- **LinkedIn limits** ([rules/linkedin-limits.md](../.github/skills/kaushal-forge/rules/linkedin-limits.md)) — headline ≤220, about ≤2600, experience ≤2000/role, title ≤100, ≤50 skills with 3 pinned, plus front-loading and `Skills:` seeding guidance. `verify.py` re-checks the headline/about lengths.
- **Fit & caps** ([rules/fit-and-caps.md](../.github/skills/kaushal-forge/rules/fit-and-caps.md)) — explains that the *script*, not the model, enforces 1-page vs 2-page. The model just provides full ranked content per variant; `render_resumes.py` auto-caps the 1-page edition (skills → first 4 rows, bullets 4/2/2/1, projects → first 2) and keeps everything for 2-page. So: order by importance, don't pad.
- **Style & voice** ([rules/style-guide.md](../.github/skills/kaushal-forge/rules/style-guide.md)) — preserve the person's authentic voice (captured in `profile.persona`), metrics over adjectives, STAR-ready bullets, ASCII only, tailor by selection not invention.

---

## The examples are the gold standard

[examples/](../.github/skills/kaushal-forge/examples/) holds a fully worked toolkit for the **fictional Asha Verma** persona (Senior Software Engineer at Acme Cloud Technologies; prior roles at Globex Systems and Initech Labs). Each phase prompt points at the matching example as the depth/structure to imitate: `master-profile.md` + `achievements-bank.md` (P1), `role-targeting-and-counsel.md` (P2), `linkedin-about.md` (P3), `variant-content.example.json` (P4 shape), `letter.example.md` (P5), `career-strategy.md` (P6). They are explicitly labelled illustrative and anonymized — all names, companies, and numbers are invented — and are there so a model can pattern-match a known-good output rather than improvise structure.

---

## The portable prompts pack — same phases, any model

[prompts/](../prompts/) is the same six phases reformatted as standalone, copy-paste prompts for *any* chat model — ChatGPT, Gemini, Sonnet, Haiku, a local model — when you don't have the Claude Code skill. **Model-agnosticism is the point:** the deterministic engine scripts are identical; only the "AI fills JSON" steps move into a chat window.

The loop is spelled out in [prompts/00-how-to-use.md](../prompts/00-how-to-use.md): set up locally (`bootstrap.py`, fill `config.yaml`, drop data in `inbox/`, `intake_dump.py`), then for each phase paste `prompts/PN-*.md` plus the required input (P1: the raw dump; P2/P3/P4/P6: `profile.json` ±`targeting.json`; P5: `variants.json`), save the model's JSON to the exact named path, and run the paired render script. Finish with `build_pdfs.py` then `verify.py` (must print `VERIFY OK`).

The pack carries the same "tips for weaker models": feed one phase at a time; if the model wraps prose around the JSON, tell it "return ONLY valid JSON, nothing else"; if `verify.py` flags a leak or length, paste the flagged item back and ask it to fix just that field. Because each portable prompt embeds its schema + a filled example, even a small model can pattern-match — the same self-contained design as the `phases/` files, just stripped of the orchestrator framing.

---

## Next

For the exact field-by-field shape of `profile.json`, `targeting.json`, `linkedin.json`, `variants.json`, and `letters.json`, see [06-data-contracts.md](06-data-contracts.md). For how the render scripts and the `verify.py` gate consume these, see [04-engine.md](04-engine.md).
