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

**Self-check before finishing:** JSON parses · every bullet traces to the dump · no GPA · no real client names · no codenames · numbers exact · persona captured.
