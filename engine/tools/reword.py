#!/usr/bin/env python3
"""KaushalForge tool — reword ONE field, safely, then re-render only what changed.

The conversational reword loop: you tell the AI "make variant 03's summary punchier";
it proposes new text; this tool applies it to exactly that field, validates the NEW text
(blocks on a mask-leak or HTML entity; warns on non-ASCII/GPA), writes the JSON back, and
re-renders the affected feed. Field-scoped so a tiny model can't drift the whole document.

  python engine/tools/reword.py get variants 03 summary
  python engine/tools/reword.py set variants 03 summary "New one-line summary."
  python engine/tools/reword.py set letters 01 body.0 "New first paragraph."
  python engine/tools/reword.py set linkedin - about.primary "New about text."

<file> = variants | letters | profile | linkedin   (id is '-' for the object files)
<dotpath> walks into the item: e.g. summary, experience.0.bullets.1, about.primary
"""
import os, sys, json, re, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/
from kf_lib import WORK, ENTITIES, LINKEDIN_LIMITS, load_cfg, get_mask

RENDER = {"variants": "render_resumes.py", "letters": "render_coverletters.py",
          "linkedin": "render_linkedin.py", "profile": None}
ARRAY_FILES = {"variants", "letters"}

def locate(data, file, vid):
    if file in ARRAY_FILES:
        items = data
        if isinstance(data, dict):
            for w in ("results", "variants", "letters"):
                if isinstance(data.get(w), list):
                    items = data[w]; break
        for it in items:
            if str((it or {}).get("id", "")) == str(vid):
                return it
        raise KeyError("no id %r in %s.json" % (vid, file))
    return data  # object files: the root is the target

def walk(obj, path, set_to=None):
    keys = [k for k in path.split(".") if k != ""]
    cur = obj
    for k in keys[:-1]:
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    last = keys[-1]
    if set_to is None:
        return cur[int(last)] if isinstance(cur, list) else cur[last]
    if isinstance(cur, list):
        cur[int(last)] = set_to
    else:
        cur[last] = set_to
    return set_to

def check_string(s, mask, dotpath):
    errs, warns = [], []
    sl = s.lower()
    for term in mask:
        if term in sl:
            errs.append("LEAK '%s'%s" % (term, " -> mask as '%s'" % mask[term] if mask[term] else ""))
    for e in ENTITIES:
        if e in s:
            errs.append("HTML entity '%s' (use the literal character)" % e)
    na = sorted({c for c in s if ord(c) > 127})
    if na:
        warns.append("non-ASCII %s (ATS/LaTeX risk)" % " ".join("U+%04X" % ord(c) for c in na))
    if re.search(r"\bGPA\b", s, re.IGNORECASE):
        warns.append("mentions GPA (house rule: omit)")
    if "about" in dotpath and len(s) > LINKEDIN_LIMITS["about"]:
        errs.append("about %d > %d chars" % (len(s), LINKEDIN_LIMITS["about"]))
    if "headline" in dotpath and len(s) > LINKEDIN_LIMITS["headline"]:
        errs.append("headline %d > %d chars" % (len(s), LINKEDIN_LIMITS["headline"]))
    return errs, warns

def main():
    a = sys.argv[1:]
    if len(a) < 4 or a[0] not in ("get", "set"):
        print(__doc__); sys.exit(2)
    op, file, vid, dotpath = a[0], a[1], a[2], a[3]
    path = os.path.join(WORK, file + ".json")
    if not os.path.exists(path):
        print("no such file: work/%s.json" % file); sys.exit(2)
    data = json.load(open(path, encoding="utf-8"))
    target = locate(data, file, vid)

    if op == "get":
        try:
            print(walk(target, dotpath))
        except Exception as e:
            print("cannot read %s: %s" % (dotpath, e)); sys.exit(2)
        return

    if len(a) < 5:
        print("set needs the new text as the 5th argument"); sys.exit(2)
    new = a[4]
    errs, warns = check_string(new, get_mask(load_cfg()), dotpath)
    for w in warns:
        print("  warn:", w)
    if errs:
        print("REWORD REJECTED — fix the new text:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    try:
        walk(target, dotpath, set_to=new)
    except Exception as e:
        print("cannot set %s: %s" % (dotpath, e)); sys.exit(2)
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("set %s.json [%s] %s" % (file, vid, dotpath))
    rscript = RENDER.get(file)
    if rscript:
        print("re-rendering via %s ..." % rscript)
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rscript)])
    print("Done. Re-run build_pdfs.py + verify.py (or run.py --from build --to verify) to refresh PDFs.")

if __name__ == "__main__":
    main()
