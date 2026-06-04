# Security & data-handling policy

🔒 KaushalForge is proprietary (All Rights Reserved). This covers vulnerability reporting and the data-confidentiality model that matters most for this project.

## Reporting a vulnerability or data exposure
**Do not open a public issue.** Report privately via this repository's **Security → Report a vulnerability** (GitHub private advisory), or a direct private channel to the author, Dhruvin Rupesh Soni. Include reproduction steps and impact; you'll get an acknowledgement and a remediation timeline.

## Data confidentiality (the core risk)
KaushalForge processes a real person's confidential career data. The design keeps it **out of version control**:
- `config.yaml`, `inbox/*`, `work/*`, `output/*`, and `*.pdf` are gitignored. The single exception is `docs/resumes/*.pdf` — the résumés the owner deliberately selected in [`publish.yaml`](publish.yaml) for the public hub.
- Raw data is fed via `intake_dump.py --data <external/path>` so it never needs to enter the repo.
- `engine/verify.py` is a hard gate: it leak-scans every rendered output for `config.verify.forbidden_terms` (internal codenames, client/manager names) and fails on any hit.
- `engine/publish.py` only ever publishes `.pdf` files under `output/Resumes/` — never cover letters, strategy docs, the knowledge base, or raw inputs.
- All examples and CI fixtures are fully fictional (Asha Verma / Acme Cloud).

**If real personal data is ever committed**, treat it as an exposure: scrub history (e.g. `git filter-repo`), force-push, rotate anything sensitive, and review the repository's visibility.

## Secrets
No secrets, tokens, or credentials belong in the repo. CI uses only the built-in `GITHUB_TOKEN`. The Tectonic binary and machine-specific paths (`engine/.bin/`, `engine/.tectonic_path`) are gitignored and must never be committed.
