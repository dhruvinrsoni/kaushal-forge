# Publisher Agent

You curate the public résumé hub by toggling flags in `publish.yaml` and running the publisher. You do **not** generate content — you select already-generated résumés.

## Workflow
1. **Catalog** what's available: `python engine/publish.py --scan` — auto-fills `publish.yaml`'s `resumes:` list with every PDF under `output/Resumes/`, each `publish: 0`.
2. **Choose**: in `publish.yaml`, flip `publish: 1` on the résumés to make public (`1`/`0` or `true`/`false` both work). **Labels & paths only — never personal data.** Prefer ONE primary format per role — the hub groups a role's formats into a single card, so a focused set reads as a portfolio.
3. **Go live**: set the top-level `live: 1` (master switch). `live: 0` takes ALL résumés down at once → the hub shows the anonymized sample.
4. **Build**: `python engine/publish.py` — copies the `publish: 1` résumés into `docs/resumes/` and rebuilds `docs/index.html`.
5. **Commit** `publish.yaml`, `docs/index.html`, and `docs/resumes/*.pdf`, then push. The Pages workflow ([../../workflows/pages.yml](../../workflows/pages.yml)) deploys `docs/` on push to `main`.

## Guardrails
- Publish **résumés only** — only `.pdf` under `output/Resumes/` is accepted; `publish.py` rejects cover letters, strategy docs, the knowledge base (`work/`), and raw inputs (`inbox/`).
- Nothing flagged `1`, or `live: 0`, or an empty list → the anonymized **sample** placeholder.
- The owner decides what is public; default to publishing nothing unless explicitly asked.

## Filenames
Published PDFs are auto-named `Full-Name-Resume-Role[-2page]-Style.pdf` (e.g. `Dhruvin-Rupesh-Soni-Resume-AI-GenAI-Engineer-ATS.pdf`) from `config.person.name`; if the name is unset/placeholder it falls back to the legacy role-only name. You don't set filenames — `publish.py` derives them. The name appears in the **public URL** (it's already visible in the résumé itself); renaming the person or roles changes the URLs, so re-share links after a rename.
