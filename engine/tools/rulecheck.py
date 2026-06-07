#!/usr/bin/env python3
"""KaushalForge tool — content-hygiene guardrail over work/*.json (the AI's output).

Catches, deterministically and BEFORE render, what the verify gate would later catch in
the PDFs: a leaked mask term, a stray HTML entity, a non-ASCII character (LaTeX/ATS risk),
a GPA mention (house rule), or an over-limit LinkedIn field. Feed its errors straight back
to the model ("fix only these"); a weak model converges because the judge is deterministic.

  python engine/tools/rulecheck.py                 # check every work/*.json present
  python engine/tools/rulecheck.py work/variants.json
Exit 0 = clean; non-zero = issues printed per location.
"""
import os, sys, json, glob, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/
from kf_lib import WORK, ENTITIES, LINKEDIN_LIMITS, load_cfg, get_mask

GPA_RE = re.compile(r"\bGPA\b", re.IGNORECASE)

def _walk_strings(obj, path=""):
    """Yield (json-path, string) for every string in a nested dict/list."""
    if isinstance(obj, str):
        yield path or "(root)", obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, "%s[%d]" % (path, i))

def check_file(path, mask):
    errs = []
    base = os.path.basename(path)
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return ["%s: invalid JSON (%s)" % (base, e)]
    for jpath, s in _walk_strings(data):
        sl = s.lower()
        for term in mask:
            if term in sl:
                repl = mask[term]
                errs.append("%s %s: LEAK '%s'%s" % (base, jpath, term,
                            " -> mask as '%s'" % repl if repl else ""))
        for e in ENTITIES:
            if e in s:
                errs.append("%s %s: HTML entity '%s' (use the literal character)" % (base, jpath, e))
        nonascii = sorted({c for c in s if ord(c) > 127})
        if nonascii:
            errs.append("%s %s: non-ASCII %s (ATS/LaTeX risk; use ASCII)"
                        % (base, jpath, " ".join("U+%04X" % ord(c) for c in nonascii)))
        if GPA_RE.search(s):
            errs.append("%s %s: mentions GPA (house rule: omit GPA)" % (base, jpath))
    if base == "linkedin.json" and isinstance(data, dict):
        for h in data.get("headline_variants", []) or []:
            txt = (h or {}).get("text", "")
            if len(txt) > LINKEDIN_LIMITS["headline"]:
                errs.append("%s: headline %d > %d chars (%s)" % (base, len(txt), LINKEDIN_LIMITS["headline"], (h or {}).get("label", "")))
        ab = data.get("about", {}) or {}
        for k in ("primary", "alt"):
            if ab.get(k) and len(ab[k]) > LINKEDIN_LIMITS["about"]:
                errs.append("%s: about.%s %d > %d chars" % (base, k, len(ab[k]), LINKEDIN_LIMITS["about"]))
    return errs

def rulecheck_work(files=None):
    if files is None:
        files = sorted(glob.glob(os.path.join(WORK, "*.json")))
    mask = get_mask(load_cfg())
    errs = []
    for f in files:
        errs += check_file(f, mask)
    return errs

def main():
    args = sys.argv[1:]
    errs = rulecheck_work(args or None)
    if errs:
        print("RULECHECK FAILED (%d):" % len(errs))
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print("RULECHECK OK — ASCII, no leaks/entities/GPA, LinkedIn limits respected.")

if __name__ == "__main__":
    main()
