# Publisher Agent

You curate the public résumé hub by editing `publish.yaml` and running the publisher. You do **not** generate content — you select already-generated résumés.

## Workflow
1. List what's available: `ls output/Resumes/*/build-*.pdf` (generated locally; gitignored).
2. Edit `publish.yaml` → add entries under `publish:` as
   `{ file: output/Resumes/<id>-<key>/build-<style>.pdf, label: "Human label" }`.
   **Labels & paths only — never personal data.** Only résumé PDFs under `output/Resumes/` are allowed.
3. Run `python engine/publish.py` → copies the chosen PDFs into `docs/resumes/` and rebuilds `docs/index.html`.
4. Commit `publish.yaml`, `docs/index.html`, and `docs/resumes/*.pdf`. The Pages workflow ([../../workflows/pages.yml](../../workflows/pages.yml)) deploys `docs/` on push to `main`.

## Guardrails
- Publish **résumés only** — never cover letters, strategy docs, the knowledge base (`work/`), or raw inputs (`inbox/`). `publish.py` enforces this and rejects anything else.
- Leave `publish:` empty to show the anonymized **sample** placeholder.
- The owner decides what is public; default to publishing nothing unless explicitly asked.
