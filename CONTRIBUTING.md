# Contributing to KaushalForge

🔒 **KaushalForge is proprietary — All Rights Reserved** (see [LICENSE](LICENSE)). It is *source-available*, **not** open source: no use, copying, modification, or distribution without the author's prior written permission. Contributions are accepted **only by prior arrangement** with the author (Dhruvin Rupesh Soni); by submitting any change you agree it is assigned to the author under the same proprietary terms. This guide is for the author and expressly authorized collaborators.

> ⚠️ **AI-assisted output.** This tool generates AI drafts that represent a real person. Never weaken the human-review gate (`reviewed: 1` in `engine/review.py` / `build_pdfs.py --approved` / `publish.py`) or the disclaimers without the author's explicit sign-off.

## Golden rule: never commit real data
- `config.yaml`, `inbox/`, `work/`, `output/`, and `*.pdf` are gitignored — keep it that way.
- Feed raw career data via `python engine/intake_dump.py --data <external/path>`, or the gitignored `inbox/`.
- The **only** public artifacts are the résumés selected in [`publish.yaml`](publish.yaml) (→ `docs/resumes/`). Never publish cover letters, strategy docs, the knowledge base, or raw inputs.
- All examples and CI fixtures stay **fully fictional** (Asha Verma / Acme Cloud). See [SECURITY.md](SECURITY.md).

## Dev workflow
1. Read [docs/](docs/README.md) first — especially [docs/07-ci-and-extending.md](docs/07-ci-and-extending.md).
2. `make dev` (deps + ruff). Quick checks: `make compile`, `make lint`.
3. Run the render-smoke in a **scratch clone** (never your live run directory) — steps in docs/07.
4. Don't finish a change until `python engine/verify.py` exits `0`.
5. **Conventional, atomic commits**: `feat: fix: docs: chore: refactor: test: ci: license:`.
6. CI (`.github/workflows/ci.yml`) must pass: `lint-validate` + the `render-smoke` gate.

## Adding things
- A new LaTeX style, AI phase, or role variant → [docs/07-ci-and-extending.md](docs/07-ci-and-extending.md).
- A new data-contract field → update the schema **and** the matching phase prompt, the portable `prompts/` copy, and a CI fixture, together. See [docs/06-data-contracts.md](docs/06-data-contracts.md).

There is intentionally **no PyPI publish workflow** — KaushalForge runs as scripts and is never packaged or published.
