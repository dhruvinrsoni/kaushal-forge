# KaushalForge documentation

**Who/what:** the guided, top-to-bottom guide to KaushalForge — start here. It takes you from "run it in 15 minutes" to a line-by-line reading of the engine, in a deliberate order. Each page is self-contained and cross-linked.

> 🔒 Proprietary & private — All-Rights-Reserved (see [LICENSE](../LICENSE)). Every example uses the fictional persona **Asha Verma / Acme Cloud**; no real personal or career data lives anywhere in this repo.

---

## What is KaushalForge?

A **repeatable, model-agnostic career-toolkit generator.** Feed it one person's raw history; it produces a LinkedIn rewrite, multi-variant LaTeX résumés (compiled to PDF, 1- and 2-page), matching cover letters, and a strategy pack — reproducibly, on any model (Opus → Haiku). The trick: split the work into **mechanical** (deterministic Python in `engine/`) and **judgement** (the AI, confined to filling rigid JSON schemas), with `engine/verify.py` as a hard gate. [02-concepts.md](02-concepts.md) explains why that makes it run on cheap models.

---

## Read in this order

| # | Guide | What you'll get | ~Time |
|---|---|---|---|
| 1 | [01-onboarding.md](01-onboarding.md) | Get a green pipeline locally in ~15 min (isolated scratch run), then the real loop and where everything lives. | 15 min |
| 2 | [02-concepts.md](02-concepts.md) | The core idea & design philosophy — mechanical vs. judgement, why weak models work, the verify gate, confidentiality, the name. | 10 min |
| 3 | [03-architecture.md](03-architecture.md) | The three layers, the `inbox → work → output` pipeline, the P1–P6 phase flow, the data-flow diagram. | 15 min |
| 4 | [04-engine.md](04-engine.md) | **Code-level** walkthrough of every `engine/` script and the four LaTeX styles. | 30 min |
| 5 | [05-ai-layer.md](05-ai-layer.md) | How the AI half works — the `kaushal-forge` skill, phases P1–P6, the rules, and the portable prompt pack. | 20 min |
| 6 | [06-data-contracts.md](06-data-contracts.md) | Field-by-field reference for `config.yaml` and the four `work/*.json` schemas, and the `output/` tree. | reference |
| 7 | [07-ci-and-extending.md](07-ci-and-extending.md) | CI jobs, the fixtures, running the smoke safely, and how to add styles / phases / variants. | 20 min |

Front-to-back is the "understand it top to bottom" path (intro → design → architecture → code → AI layer → contracts → CI/extending).

---

## Jump by goal

- **"I just want to run it for someone."** → [01-onboarding.md](01-onboarding.md), then the operator's step-by-step in [../RUNBOOK.md](../RUNBOOK.md); reach for [06-data-contracts.md](06-data-contracts.md) if a phase output is rejected.
- **"I want to understand the whole system."** → [02-concepts.md](02-concepts.md) → [03-architecture.md](03-architecture.md) → [04-engine.md](04-engine.md) → [05-ai-layer.md](05-ai-layer.md).
- **"I'm changing the engine / adding a style or phase."** → [04-engine.md](04-engine.md) + [06-data-contracts.md](06-data-contracts.md) + [07-ci-and-extending.md](07-ci-and-extending.md).
- **"Why does it work on cheap models, and is it safe?"** → [02-concepts.md](02-concepts.md).

---

## Related top-level docs

| Doc | Role |
|---|---|
| [../README.md](../README.md) | Project front page + 60-second quickstart. |
| [../RUNBOOK.md](../RUNBOOK.md) | The operator's phase-by-phase runbook (what to run, in order). |
| [../MASTER-PLAN.md](../MASTER-PLAN.md) | The original design spec & rationale (how and why it was built). |
| [../CLAUDE.md](../CLAUDE.md) | Context loaded by Claude Code when working in this repo. |
| [../CHANGELOG.md](../CHANGELOG.md) | Notable changes. |

This `docs/` suite is the *reader's* path; `MASTER-PLAN.md` is the *builder's* spec. They overlap on purpose — the docs add depth (code-level, contracts, CI) that the spec only summarizes.

---

**Next:** [01-onboarding.md](01-onboarding.md).
