# Portable prompt pack — run KaushalForge with ANY model (no Claude needed)

Use this when you don't have Claude Code / the skill — e.g. ChatGPT, Gemini, a local model, Sonnet, or Haiku. The deterministic scripts are identical; only the "AI fills JSON" steps move into your chat window.

## Loop
1. **Setup locally:** `python engine/bootstrap.py`; fill `config.yaml`; put data in `inbox/`; `python engine/intake_dump.py`.
2. For each phase P1→P6:
   - Open `prompts/PN-*.md`, copy it into your model's chat.
   - Paste the required input after it (P1: the contents of `work/00-raw-dump.txt`; P2/P3/P4/P6: your `work/profile.json` (+`targeting.json`); P5: your `work/variants.json`).
   - The model returns **only JSON** (P6 returns markdown files). Save it to the exact path the prompt names (e.g. `work/profile.json`).
   - Run the paired script: `python engine/render_linkedin.py` / `render_resumes.py` / `render_coverletters.py` / `render_strategy.py`.
3. **Build + gate:** `python engine/build_pdfs.py` then `python engine/verify.py` (must print `VERIFY OK`).

## Human checkpoints — don't skip (this is a real person)
Everything the model returns is an **AI draft you must review and own**. Stop and read before moving on:
- **After P1 (`profile.json`)** — the foundation. Read it; fix anything wrong before P2 (a bad profile poisons every résumé).
- **After P2 (`targeting.json`)** — confirm the roles/direction are right before drafting content.
- **Before the final build / publishing** — run `python engine/review.py`, read `work/REVIEW.md`, fix any `work/*.json`, then set **`reviewed: 1`** in `work/review.yaml`. `build_pdfs.py --approved` and `publish.py` **refuse until you do** — that flag is your sign-off that you own this content.

## The validate-and-retry loop (makes even a ~1B local model work)
After you save each `work/*.json`, run the deterministic guardrails and feed their output straight back to the model:
```
python engine/tools/validate.py    # does the JSON conform to the schema? (exact field paths)
python engine/tools/rulecheck.py   # ASCII only? no mask-leaks / HTML entities / GPA? LinkedIn limits?
```
If either prints errors, paste them to the model with **"fix only these fields, return the whole JSON again,"** and re-save. Repeat until both print `OK`. The script is the judge, so the model only has to *converge* — it doesn't have to be right first try. `verify.py` runs `validate.py` again at the end as a backstop.

## Tips for weaker models
- Feed **one phase at a time**, and within a phase fill the file in **small passes** (e.g. P1: identity+summary, then experience, then the rest, then `achievements_bank`) — validate after each pass.
- If the model adds prose around the JSON, tell it "return ONLY valid JSON, nothing else," then re-save.
- Use `python engine/tools/achievements.py <keywords>` to find the real bullets to reuse — never let the model invent numbers.
- The schemas + a filled example are inside each prompt, so even a small model can pattern-match.

## Reword one field, conversationally (full control, no drift)
To tweak a single field afterward, ask the model for new text for just that field, then apply it safely (it validates the new text and re-renders only that feed):
```
python engine/tools/reword.py get variants 03 summary
python engine/tools/reword.py set variants 03 summary "Your punchier one-line summary."
```
It blocks the change if the new text leaks a masked term or contains an HTML entity. Then rebuild: `python engine/build_pdfs.py && python engine/verify.py`.

The 6 prompts: `P1-structure`, `P2-targeting`, `P3-linkedin`, `P4-resumes`, `P5-coverletters`, `P6-strategy`. Each is self-contained.
