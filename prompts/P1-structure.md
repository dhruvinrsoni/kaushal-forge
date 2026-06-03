You are a meticulous career analyst. I will paste a raw dump of one person's career data (LinkedIn export, performance reviews, resume, GitHub text, etc.). Turn it into ONE clean, confidentiality-safe JSON knowledge base.

RULES (strict):
- Omit GPA/CGPA. Generalise client names to a category (e.g. "Fortune-500 retail"). Strip internal codenames/product names but KEEP the metrics. Frame AI-assisted work as "AI-augmented engineering."
- NEVER fabricate — every claim, metric, title, date must come from the dump. Keep numbers exact. ASCII only.
- Capture the person's authentic voice in "persona".

Return ONLY valid JSON (save as work/profile.json) with this shape:
{
 "identity": {"name","pronouns","location","tagline","handles":{}},
 "headline": "master résumé headline (one line)",
 "summary": "master résumé 2-4 line summary",
 "focus": "optional one-line focus or \"\"",
 "experience": [{"role","org","dates","location","bullets":["…"]}],
 "education": [{"degree","institution","dates","detail"}],
 "skills_groups": [{"label","items":"comma-separated"}],
 "certs": ["…"], "awards": ["…"], "languages": ["…"],
 "projects": [{"name","meta","desc","url"}],
 "persona": "voice/motivations to preserve",
 "achievements_bank": ["every quantified, codename-free, client-safe, résumé-ready bullet"]
}

After the JSON, list separately (for me, not in the JSON) any internal codenames / client names / manager & peer names you stripped, so I can add them to a leak-scan list.

=== PASTE work/00-raw-dump.txt BELOW ===
