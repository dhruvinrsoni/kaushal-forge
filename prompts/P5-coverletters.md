You are an expert cover-letter writer. From the variants JSON + profile JSON (pasted below), write ONE tailored cover letter per variant id (also include id "09" key "master-general" = an all-purpose letter).

A cover letter is PRIVATE (sent to a target employer) — so it MAY express genuine interest in the role and openness to relocation. Confident, specific, warm; never desperate or boastful. ~250-330 words, 3-4 short paragraphs. ASCII only. Use bracket placeholders [Company], [Role], [Hiring Manager], and a [why-this-company] hook. Lead the proof paragraph with the achievement most relevant to that archetype; numbers exact; trace to profile.

Return ONLY a valid JSON ARRAY (save as work/letters.json); one object per variant:
{ "id","key","email_subject","opening (specific hook, NOT \"I am writing to apply\")",
  "body":["1-2 proof paragraphs"], "closing (confident CTA)",
  "why_company_prompt":"instruction telling the candidate exactly what specific researched detail to put in the [why-this-company] slot",
  "notes_md":"when to use · what to customize · tone" }

=== PASTE work/variants.json AND work/profile.json BELOW ===
