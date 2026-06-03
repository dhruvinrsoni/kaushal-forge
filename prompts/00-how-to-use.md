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

## Tips for weaker models
- Feed **one phase at a time**; don't ask for everything at once.
- If the model adds prose around the JSON, tell it "return ONLY valid JSON, nothing else," then re-save.
- If `verify.py` flags a leak/length, paste the flagged item back and ask the model to fix just that field.
- The schemas + a filled example are inside each prompt, so even a small model can pattern-match.

The 6 prompts: `P1-structure`, `P2-targeting`, `P3-linkedin`, `P4-resumes`, `P5-coverletters`, `P6-strategy`. Each is self-contained.
