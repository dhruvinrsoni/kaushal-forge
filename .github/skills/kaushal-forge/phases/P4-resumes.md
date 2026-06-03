# P4 — Résumé content (the proven résumé-drafting prompt)

**Role:** Expert technical résumé writer + recruiter. Draft tailored **structured content** (NOT LaTeX) for each target variant + its GUIDE.

**Read:** `work/profile.json` (use `identity`, `experience` exact titles/orgs/dates, `achievements_bank`, `education`, `certs`, etc.) and `work/targeting.json` (`variant_list` + each role's `emphasise`/`best_style`). **Write:** `work/variants.json` (a JSON array).

**Per variant, return an object** (`schemas/variants.schema.json`):
`{ id, key, headline, summary, focus, skills_rows[{label,items}], experience[{role,org,dates,location,bullets[]}], projects[{name,meta,desc}], guide_md }`
(Do **not** emit id `09` — the Master is auto-built from profile.json by the script.)

**Rules (from the proven session):**
- Plain ASCII only (write `$0`, `~80x`, `10-15%`, `->`). No LaTeX — the script escapes.
- Tailor by **selection, ordering, light rephrasing** of `achievements_bank` items to the target's keywords. Never fabricate; keep numbers exact. Apply `rules/confidentiality.md`.
- Use **exact** titles/orgs/dates from `profile.json`.
- **Order content by importance** (the script auto-caps the 1-page edition: skills→4 rows, bullets current 4 then 2/2/1, projects→2; 2-page keeps all). So put the strongest first.
- `headline`: 2–3 segments separated by " | ". `summary`: 2–4 punchy lines. `focus`: short interests line or "".
- `guide_md`: when to use · target-JD keywords · honest fit/odds + any gap · which style (ats/modern/twocol) suits + why · 2–3 tweak tips.

**Default variant briefs** (use `targeting.json` to adjust; these are the proven archetypes):
- **01 software-engineer-backend** — Senior/Backend SWE. Lead with core backend (language/frameworks/microservices), flagship product work, REST, data, system design, reliability; AI as a secondary "modernization" note. Safest/broadest.
- **02 cloud-devops-platform** — Cloud/DevOps/Platform/SRE. Lead with cloud platform, Kubernetes/CI-CD, reliability metrics (zero incidents/regressions, hotfix), migrations, cost cuts, DevSecOps.
- **03 ai-genai-engineer** — Applied AI/GenAI/LLM. Lead with AI/agent/LLM work + MCP/RAG + AI-related OSS; backend/cloud as the "production-grade engineer who also ships AI" base. Add a focus line.
- **04 ai-devtools-agentic** — Dev-tools/Agentic/DevEx. Lead with agentic automation, agent/skill frameworks, DevEx velocity, the most builder-y OSS. Frame "tools that make engineers faster + safer." Add focus.
- **05 solutions-cloud-architect** — Architect. Lead with architecture transformations, migrations under constraint, security architecture, cross-functional orchestration, cost/capacity; fewer code-level bullets, more design/impact. (Often a dense variant → set `cap_overrides:{ "05":3 }`.)
- **06 staff-ai-first-engineer** — Staff/Lead. Lead with force-multiplier/org-wide leverage (knowledge forums, SOPs, velocity, mentoring), then technical depth. Confident senior voice.
- **07 research-engineer-ai** — Research/ML Engineer (applied/infra). Lead with math foundation + experimentation rigor + R&D + OSS test rigor; add a "Research interests" focus line; if a gap (no PhD/pubs) note it in guide_md and target Engineer not Scientist.
- **08 forward-deployed-mts** — FDE/MTS. Lead with end-to-end ownership, ship-under-constraints, customer-facing wins, generalist breadth + OSS autonomy.
- **10 counsellors-pick** — the recommended bet from `targeting.counsel`. The sharpest, most opinionated 1-pager; foreground the person's rarest combination of strengths; add a strong focus line; include a short "why this is the bet" in guide_md.

**Gold examples:** `examples/variant-content.example.json` (shape) + the `examples/*.md`.

**Then run:** `python engine/render_resumes.py` → `output/Resumes/**`.

**Self-check:** JSON array parses · each object has all required keys · ASCII only · titles/dates match profile · ids match `variant_list` minus 09.
