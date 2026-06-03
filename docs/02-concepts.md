# Core concepts & design philosophy

**Who/what:** For anyone who wants to understand *why* KaushalForge is built the way it is before learning *how* to run it. This doc is about ideas and rationale; the operator steps live in [../RUNBOOK.md](../RUNBOOK.md) and the full spec in [../MASTER-PLAN.md](../MASTER-PLAN.md).

🔒 KaushalForge is proprietary, private, and author-owned (see [../LICENSE](../LICENSE)). Nothing here invites external use or contribution.

---

## The one idea: split mechanical work from judgement

KaushalForge generates a complete career toolkit — a LinkedIn rewrite, multi-variant LaTeX résumés compiled to PDF, matching cover letters, and a strategy pack — from one person's raw data. The whole design rests on a single decision: **separate the work that needs zero intelligence from the work that needs judgement, and never let them mix.**

- **MECHANICAL** — rendering LaTeX, compiling PDFs, counting characters, scanning for leaks, checking page counts. This is deterministic and identical on any machine, so it is handled entirely by Python scripts in [../engine/](../engine/). No model touches it.
- **JUDGEMENT** — writing the tailored content (what to say, which achievements to lead with, how to phrase a headline). This is the only part the AI does, and it is **confined to filling rigid JSON schemas**, with a worked example sitting beside each schema as a pattern to imitate.

The AI never emits LaTeX, never decides page layout, never counts anything. It emits structured JSON or templated markdown; every render, compile, and check is a script. [../MASTER-PLAN.md](../MASTER-PLAN.md) calls this "the whole trick," and the scope guardrails make it a hard rule: *keep the engine deterministic; keep AI confined to schema-filling.*

### Why this lets it run on cheap models (Opus → Haiku)

A blank-page generative task ("write me a great résumé") rewards a strong model and punishes a weak one — a small model fills the gaps by inventing. KaushalForge removes the blank page. Each judgement step is reframed as a bounded **"fill this exact schema, like this exact example"** task:

- The shape is fixed by a schema in [.github/skills/kaushal-forge/schemas/](../.github/skills/kaushal-forge/schemas/) (`profile`, `variants`, `letters`, `linkedin`).
- A gold reference sits in [.github/skills/kaushal-forge/examples/](../.github/skills/kaushal-forge/examples/) — e.g. `master-profile.md`, `variant-content.example.json`, `linkedin-about.md` — so the model **pattern-matches instead of inventing**.
- Each phase prompt ([.github/skills/kaushal-forge/phases/](../.github/skills/kaushal-forge/phases/), P1–P6) carries its role, inputs, schema, rules, a worked example, and self-checks inline, so it is self-contained enough for a Haiku-class model.

The same artifacts also drive the portable copy-paste pack in [../prompts/](../prompts/), so the capability survives even without Claude or Opus. The point of the original session (hand-built on Opus 4.8) was to *encapsulate* that quality so it can be re-run six months later on whatever model is cheap and available. The quality floor stays high because the structure, not the model, carries most of the weight.

---

## The verify.py hard gate: the safety net

A weak model will still slip. The design's answer is not a stronger model — it is a deterministic gate that fails the build when a slip reaches the output. [../engine/verify.py](../engine/verify.py) **exits non-zero on any failure**, so it is a real gate, not a warning. A run is not "done" until `verify.py` exits 0 and prints `VERIFY OK`.

It checks four things, all mechanical:

1. **Leak scan** — every term in `config.verify.forbidden_terms` (codenames, client names, manager/peer names) is searched, case-insensitively, across résumé `content.tex`, cover-letter `letter.tex`/`letter.md`, LinkedIn `*.md`, and Strategy `*.md` ([verify.py:22-34](../engine/verify.py)). Any hit is a `LEAK` failure.
2. **Stray HTML entities** — the same files are scanned for `&gt; &lt; &amp; &#39; &quot;` ([verify.py:23](../engine/verify.py)); these signal an escaping miss and fail the build.
3. **LinkedIn char limits** — read from `work/linkedin.json`: each headline variant must be ≤ 220 chars and `about.primary` / `about.alt` ≤ 2600 ([verify.py:38-45](../engine/verify.py)).
4. **PDF page counts** — via `pypdf`: role résumés must be 1 page; any `*-2page` folder or the `09`-master must be 2; every cover letter must be 1 ([verify.py:48-57](../engine/verify.py)). (If `pypdf` is absent, this single check is skipped with a printed note.)

This is why the engine can stay dumb: the judgement layer is allowed to be imperfect because a deterministic gate catches the specific, enumerable ways it goes wrong (leaks, bad escaping, over-length, wrong page count) before anything ships.

---

## Confidentiality, diplomacy, and the honesty rule

These principles are enforced at the judgement layer and re-checked at the gate. They are summarized from [.github/skills/kaushal-forge/rules/confidentiality.md](../.github/skills/kaushal-forge/rules/confidentiality.md).

**Confidentiality.** Client names are generalized to a category (e.g. a real retailer becomes "Fortune-500 retail & pharmacy clients"); internal codenames and system names are stripped **while the metrics are kept** (e.g. a named internal service's coverage figure stays, the name goes); AI-assisted work is framed professionally as "AI-augmented engineering"; GPA/CGPA is omitted on experienced résumés. Crucially, the person's actual codenames, client names, and manager/peer names go into `config.verify.forbidden_terms` so the gate hard-fails if any leak through.

**Diplomatic model.** When `config.targets.diplomatic` is true, nothing *public* — LinkedIn above all — may imply job-seeking, leaving the employer, or relocating out. Public content is framed as curiosity, craft, and impact; the tone rule in [.github/skills/kaushal-forge/rules/linkedin-limits.md](../.github/skills/kaushal-forge/rules/linkedin-limits.md) forbids words like "seeking / open to / relocating / available." The asymmetry is deliberate: cover letters are *private* documents sent to a target employer, so there expressing interest in the role and openness to relocation is fine.

**The honesty rule.** No fabrication. Every claim, metric, title, and date must trace to `work/00-raw-dump.txt`; if something is unknown it is omitted, never invented, and all numbers stay exact. The style guide reinforces this from the other side: tailoring happens by **selection and ordering**, not invention — the model picks and lightly rephrases items from the person's `achievements_bank` to match a target role, rather than manufacturing new ones ([.github/skills/kaushal-forge/rules/style-guide.md](../.github/skills/kaushal-forge/rules/style-guide.md)). The same file also preserves the person's authentic voice (captured in `profile.persona`) and prefers metrics over adjectives, so the output is honest *and* distinctive, not a flattened template.

A related division of labor: the model never decides what *fits* on a page. It supplies full, importance-ordered content; [../engine/render_resumes.py](../engine/render_resumes.py) applies the 1-page caps and 2-page full mode ([.github/skills/kaushal-forge/rules/fit-and-caps.md](../.github/skills/kaushal-forge/rules/fit-and-caps.md)). This keeps the mechanical/judgement line clean even for layout.

---

## The name

**KaushalForge** = *kaushal* (Sanskrit कौशल — skill, craftsmanship, proficiency) + *Forge*. The name encodes the thesis: skill (the judgement, the craft of a strong career narrative) is captured once and then **forged** repeatably — hammered into a fixed, durable shape by deterministic tooling so it can be reproduced on demand, on any model, without losing its temper.

---

## Next

Continue to [03-architecture.md](03-architecture.md) for how the three layers and the phase pipeline fit together, or jump to [04-engine.md](04-engine.md) for the deterministic scripts and [05-ai-layer.md](05-ai-layer.md) for the skill, phases, and schemas.
