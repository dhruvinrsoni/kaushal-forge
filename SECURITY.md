# Security & data-handling policy

> ⚠️ **AI-assisted output.** KaushalForge generates AI drafts of a real person's résumés/letters/profile. They are **not verified fact** — a human must review, correct, and **own every claim** before anything is sent or published. The engine enforces a review sign-off (`reviewed: 1`) before the approved build or any publish; see "Human review gate" below / `engine/review.py`.

🔒 KaushalForge is proprietary (All Rights Reserved). This covers vulnerability reporting and the data-confidentiality model that matters most for this project.

## Reporting a vulnerability or data exposure
**Do not open a public issue.** Report privately via this repository's **Security → Report a vulnerability** (GitHub private advisory), or a direct private channel to the author, Dhruvin Rupesh Soni. Include reproduction steps and impact; you'll get an acknowledgement and a remediation timeline.

## Data confidentiality (the core risk)
KaushalForge processes a real person's confidential career data. The design keeps it **out of version control**:
- `config.yaml`, `inbox/*`, `work/*`, `output/*`, and `*.pdf` are gitignored. The single exception is `docs/resumes/*.pdf` — the résumés the owner deliberately selected in [`publish.yaml`](publish.yaml) for the public hub.
- Raw data is fed via `intake_dump.py --data <external/path>` so it never needs to enter the repo.
- **Single source of truth:** `config.verify.mask` (gitignored) maps each sensitive term → its public-safe replacement.
- `engine/verify.py` is a hard gate: it leak-scans those terms across generated **outputs *and* tracked source files**, failing on any hit (and printing the suggested mask).
- A **pre-commit hook** (`.githooks/`, installed by `engine/bootstrap.py`) blocks any commit whose staged content (text or PDF visible-text) contains a term — the leak is stopped before it's committed.
- `engine/publish.py` only ever publishes `.pdf` files under `output/Resumes/` — never cover letters, strategy docs, the knowledge base, or raw inputs.
- Published résumé **filenames embed `config.person.name`** (e.g. `Dhruvin-Rupesh-Soni-Resume-...pdf`), so the name is visible in the public URL — by design (the name is already on the résumé), and only for résumés the owner explicitly flagged. Falls back to a role-only name when the config name is unset.
- **Cover letters are not publishable, with one explicit exception:** `publish.yaml: letter_sample: 1` may publish the SINGLE generic, company-agnostic master letter (`output/CoverLetters/09-master-general/letter.pdf`) to `docs/letters/` as a writing sample. This is enforced by a separate `safe_letter_sample()` allowlist that accepts only a `*-general` letter — it never relaxes the résumé whitelist, and **per-company letters can never be published**. Default is off.
- All examples and CI fixtures are fully fictional (Asha Verma / Acme Cloud).

**If real personal data is ever committed**, treat it as an exposure: scrub history (e.g. `git filter-repo`), force-push, rotate anything sensitive, and review the repository's visibility.

## Secrets
No secrets, tokens, or credentials belong in the repo. CI uses only the built-in `GITHUB_TOKEN`. The Tectonic binary and machine-specific paths (`engine/.bin/`, `engine/.tectonic_path`) are gitignored and must never be committed.
