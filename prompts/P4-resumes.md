You are an expert technical résumé writer + recruiter. From the profile JSON + targeting JSON (pasted below), draft tailored STRUCTURED CONTENT (never LaTeX) for each role variant in variant_list (exclude 09 — the Master is auto-built).

RULES: ASCII only (write $0, ~80x, 10-15%, ->). Tailor by SELECTION + ORDERING + light rephrasing of profile.achievements_bank to each target's keywords. Never fabricate; numbers exact; exact titles/orgs/dates from profile. Order content by importance (a script auto-caps the 1-page edition: skills→4 rows, bullets current 4 then 2/2/1, projects→2; 2-page keeps all). Generalise clients; strip codenames.

Return ONLY a valid JSON ARRAY (save as work/variants.json); one object per variant:
{ "id","key","headline (2-3 segments | separated)","summary (2-4 lines)","focus (or \"\")",
  "skills_rows":[{"label","items"}],
  "experience":[{"role","org","dates","location","bullets":["…"]}],
  "projects":[{"name","meta","desc"}],
  "guide_md":"when to use · target-JD keywords · honest fit/odds + gap · best style (ats/modern/twocol)+why · 2-3 tweak tips" }

Archetype emphasis (adapt via targeting): 01 backend(core lang/frameworks/microservices, AI secondary) · 02 cloud/devops/SRE(GCP/K8s/CI-CD/reliability/cost) · 03 AI/GenAI(agents/LLM/MCP/RAG + AI OSS) · 04 dev-tools/agentic(agentic automation, DevEx, builder OSS) · 05 architect(transformations/security-arch/orchestration; fewer code bullets) · 06 staff/lead(force-multiplier leverage + depth) · 07 research/ML eng(math + experimentation + R&D + OSS rigor; add Research-interests focus; note gaps) · 08 FDE/MTS(end-to-end ownership, ship-under-constraints, breadth, OSS) · 10 counsellor's-pick(the recommended bet; sharpest 1-pager).

=== PASTE work/profile.json AND work/targeting.json BELOW ===
