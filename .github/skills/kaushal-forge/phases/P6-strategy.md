# P6 — Strategy pack

**Role:** Career mentor. Write the durable strategy docs (plain markdown the operator reads).

**Read:** `work/profile.json` + `work/targeting.json`. **Write:** markdown files into `work/strategy/` (the renderer copies them to `output/Strategy/`).

**Produce these files** (adapt to the person; honest, specific, no hype):
- `career-strategy.md` — per-role market read (titles, who hires, honest odds, rough comp bands by geo *with a "verify" caveat*), the credential/brand-gap analysis, and a sequenced 6–18 month plan.
- `global-visibility-playbook.md` — if `targets.diplomatic`: how to be discoverable to recruiters without signalling job-search (recruiters-only Open-to-Work, inbound-pull via content/OSS, outreach scripts, what-not-to-do). Else: a straightforward visibility plan.
- `online-masters-bridge.md` — if relevant to the person/targets: online MS options (cost, specialization, work-compatibility) and the honest visa nuance (online ≠ F-1/OPT; helps points-systems & H-1B master's-cap).
- `in-person-masters-usa.md` — if US relocation is a target: F-1→OPT→STEM-OPT→H-1B chain, program tiers, and the full menu of routes (in-person MS, direct sponsorship, O-1, Canada Express Entry). Always add "consult an immigration attorney."
- `target-companies.md` — visa-sponsoring, fit-ranked companies/categories mapped to the variants, with a "verify sponsorship" note and where-to-look list.
- `interview-prep.md` — the interview loops, a per-track plan, **ready STAR stories built from the person's real metrics** (mine `profile.achievements_bank`), a schedule, and resources.

**Rules:** honesty over flattery; cite the person's real metrics in the STAR stories; respect diplomacy; never invent comp/visa facts — frame as directional + "verify."

**Gold example:** `examples/career-strategy.md`.

**Then run:** `python engine/render_strategy.py` → `output/Strategy/`.

**Self-check:** files written to `work/strategy/` · STAR stories use real (traceable) metrics · visa/comp claims carry a verify caveat.
