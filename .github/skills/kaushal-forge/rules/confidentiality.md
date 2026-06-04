# Confidentiality & honesty rules (apply to EVERYTHING)

1. **Omit GPA/CGPA** on experienced résumés (5+ yrs). Keep only if specifically asked.
2. **Generalise client names** to a category — e.g., "RetailCo / PharmaChain" → "Fortune-500 retail & pharmacy clients." Never name real clients.
3. **Strip internal codenames** (project/product/tool codenames, internal system names) but **keep the metrics**. e.g., "bluefalcon-api coverage" → "an internal service's coverage."
4. **Frame AI-assisted work professionally:** "vibe coding" / "AI-assisted" → "AI-augmented engineering."
5. **Diplomacy (if `config.targets.diplomatic` is true):** nothing *public* (LinkedIn especially) may imply job-seeking, leaving the employer, or relocating-out. Frame as curiosity / craft / impact. (Cover letters are private documents sent to a target employer — there it's fine to express interest in the role and openness to relocation.)
6. **No fabrication.** Every claim, metric, title, and date must trace to `work/00-raw-dump.txt`. If unknown, omit — never invent. Keep all numbers exact.
7. **Add the person's internal codenames / client names / manager & peer names to `config.verify.mask`** (term → safe replacement). `verify.py` hard-fails on any leak in outputs **or tracked files**, and a pre-commit hook blocks them at commit time.
