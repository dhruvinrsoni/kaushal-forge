# LinkedIn character limits & section rules

| Section | Hard limit | Aim for |
|---|---|---|
| Headline | 220 | 180–219 |
| About / Summary | 2,600 | 2,000–2,580 |
| Experience description (each role) | 2,000 | 1,500–1,990 |
| Job title | 100 | as needed |
| Skills | 50 total | fill ~40–50; **pin 3** |

- Provide **3–4 headline variants** (each ≤220) tuned to different target clusters.
- About: front-load the hook in the first ~2 lines (the rest is truncated behind "…see more").
- Each experience role: 1-line context + metric-led bullets + a trailing `Skills:` line (seeds search).
- Skills: order so the most-searched target skills lead; name the 3 to pin.
- `verify.py` re-checks headline/about lengths from `work/linkedin.json` and fails if over limit.
- Diplomatic tone throughout (see confidentiality rule 5): never "seeking / open to / relocating / available."
