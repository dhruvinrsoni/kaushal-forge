# P1 — Structure & clean (data-mining the dump into profile.json)

**Role:** You are a meticulous career analyst. Turn messy raw data into one clean, structured, confidentiality-safe knowledge base.

**Read:** `work/00-raw-dump.txt` (everything the person provided). **Write:** `work/profile.json`.

**Apply:** `rules/confidentiality.md` (omit GPA; generalise client names; strip codenames; no fabrication; diplomacy) and `rules/style-guide.md` (metrics over adjectives; preserve voice).

**Do:**
1. Extract canonical **identity, contact handles, experience (exact titles/orgs/dates/location + bullets), education, skills (grouped), certs, awards, languages, projects, persona.**
2. Build an **`achievements_bank`**: every quantified, codename-free, client-safe, résumé-ready bullet you can mine — these are the raw material P4/P5 will select from. Keep numbers exact.
3. Write a master **`headline`** (one line) and **`summary`** (2–4 lines) for the master résumé.
4. **Collect (for the operator) any internal codenames / client names / manager & peer names you stripped** — list them at the end of your message so they can be added to `config.verify.mask`.

**Schema:** `schemas/profile.schema.json`. **Gold example:** `examples/master-profile.md` + `examples/achievements-bank.md` (this is the depth/structure to match).

**Output:** valid JSON only, to `work/profile.json`. ASCII text (no LaTeX).

## Work in small, validated passes (this is how a tiny/local model succeeds)
Don't write the whole file in one shot. Fill it in fragments, copying the example's shape exactly, and let the **scripts be the judge** after each pass:
1. **identity + headline + summary** -> write `work/profile.json` with just those keys.
2. **experience** (exact titles/orgs/dates/location + bullets) -> add the array.
3. **education, skills_groups, certs, awards, languages, projects, persona** -> add them.
4. **achievements_bank** -> mine every quantified, safe bullet last.

After each pass, run the guardrails and **fix only the fields they name** — repeat until both are clean:
```
python engine/tools/validate.py work/profile.json     # missing/wrong-typed fields, with exact path
python engine/tools/rulecheck.py work/profile.json    # non-ASCII, mask leaks, HTML entities, GPA
```
Output ONLY JSON (no prose, no LaTeX, no markdown fences). If a tool reports `[2].bullets: expected array`, fix exactly that and re-run — you don't have to be right first try, you have to converge.

**Self-check before finishing:** `validate.py` + `rulecheck.py` both pass · every bullet traces to the dump · no GPA · no real client names · no codenames · numbers exact · persona captured.

## STOP — hand to the human (mandatory)
`profile.json` is the foundation every résumé/letter is built from, so a mistake here poisons everything. After it validates, **STOP**: give the operator a short plain-language summary (who this says they are; the experience, skills, and achievements you captured; anything you generalised or dropped) and the codename/client/name list to add to `config.verify.mask`. **Wait for their explicit "continue"** before starting P2. Do not proceed on your own.
