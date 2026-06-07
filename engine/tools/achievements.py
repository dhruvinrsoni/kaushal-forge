#!/usr/bin/env python3
"""KaushalForge tool — search the profile's achievements_bank by keyword.

Anti-fabrication aid: when a phase needs a bullet for a target role, it SELECTS from
real, already-vetted achievements instead of inventing one. Ranks bank entries by how
many of the given keywords they contain (case-insensitive substring).

  python engine/tools/achievements.py kubernetes cost latency
  python engine/tools/achievements.py            # list the whole bank
Reads work/profile.json (falls back to tests/fixtures/profile.json for a dry run).
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/
from kf_lib import WORK, ROOT

def load_bank():
    for p in (os.path.join(WORK, "profile.json"),
              os.path.join(ROOT, "tests", "fixtures", "profile.json")):
        if os.path.exists(p):
            try:
                return json.load(open(p, encoding="utf-8")).get("achievements_bank", []) or [], p
            except Exception:
                pass
    return [], None

def search(bank, keywords):
    if not keywords:
        return [(0, b) for b in bank]
    kws = [k.lower() for k in keywords]
    scored = []
    for b in bank:
        bl = b.lower()
        hits = sum(1 for k in kws if k in bl)
        if hits:
            scored.append((hits, b))
    return sorted(scored, key=lambda x: -x[0])

def main():
    kws = sys.argv[1:]
    bank, src = load_bank()
    if not bank:
        print("No achievements_bank found (run P1 to write work/profile.json).")
        sys.exit(1)
    results = search(bank, kws)
    print("achievements_bank from %s (%d entries%s):"
          % (os.path.relpath(src, ROOT), len(bank), "; matching: %d" % len(results) if kws else ""))
    for hits, b in results:
        print(("  [%d] " % hits if kws else "  - ") + b)
    if kws and not results:
        print("  (no matches — pick the closest real bullet; never fabricate)")

if __name__ == "__main__":
    main()
