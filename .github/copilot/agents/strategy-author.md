# Strategy Author Agent

You write the job-search strategy pack as markdown files in `work/strategy/` — Phase **P6**. This phase emits **markdown**, not JSON; the engine copies it through with an index.

## Workflow
1. Read `work/profile.json` and `work/targeting.json`.
2. Open `.github/skills/kaushal-forge/phases/P6-strategy.md` and follow it exactly (it names the documents to produce and the gold example).
3. Write one or more `.md` files into `work/strategy/` (e.g. `career-strategy.md`) — a concrete plan grounded in the targeting counsel: which roles, in what order, how to close named gaps, outreach/application sequencing.
4. Confidentiality-safe and honest: no real client names or codenames, no fabricated facts. ASCII only.
5. Write the files, then render. (`rulecheck.py`/`validate.py` are JSON-only — they don't apply to markdown; the leak/entity scan for strategy output is done by `verify.py` at the gate.)
   ```
   python engine/render_strategy.py
   ```

## Output
`work/strategy/*.md` → `output/Strategy/` (with `00-index.md`). `verify.py` scans these for masked-term leaks and stray entities at the gate.
