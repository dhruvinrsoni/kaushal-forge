#!/usr/bin/env python3
"""KaushalForge — compile every résumé build-*.tex and cover-letter letter.tex with Tectonic.
Prints a pass/fail + page-count table. Exit non-zero if any compile fails.

  python engine/build_pdfs.py              # build everything (default; CI uses this)
  python engine/build_pdfs.py --approved   # build only ids flagged approve:1 in work/review.yaml
"""
import os, re, sys, glob, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output")

def _to_bool(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v.strip().lower() in ("1", "true", "yes", "on", "y")
    return False

def approved_ids():
    """(resume_ids, letter_ids) approved in work/review.yaml; (None, None) if no usable review file."""
    path = os.path.join(ROOT, "work", "review.yaml")
    try:
        import yaml
        d = yaml.safe_load(open(path, encoding="utf-8")) or {}
    except Exception:
        return None, None
    if not (d.get("resumes") or d.get("letters")):
        return None, None
    def collect(key):
        return {str(r.get("id")) for r in (d.get(key) or [])
                if isinstance(r, dict) and _to_bool(r.get("approve"))}
    return collect("resumes"), collect("letters")

def folder_id(tex):
    m = re.match(r"(\d+)-", os.path.basename(os.path.dirname(tex)))
    return m.group(1) if m else None

def tectonic():
    p = os.environ.get("CAREERFORGE_TECTONIC")
    if p and os.path.exists(p): return p
    f = os.path.join(HERE, ".tectonic_path")
    if os.path.exists(f):
        c = open(f, encoding="utf-8").read().strip()
        if c and os.path.exists(c): return c
    w = shutil.which("tectonic")
    if w: return w
    for c in (os.path.join(HERE, ".bin", "tectonic.exe"), os.path.join(HERE, ".bin", "tectonic")):
        if os.path.exists(c): return c
    return None

def pages(pdf):
    try:
        import pypdf
        return len(pypdf.PdfReader(pdf).pages)
    except Exception:
        return "?"

def main():
    tec = tectonic()
    if not tec:
        print("ERROR: Tectonic not found. Run: python engine/bootstrap.py  (or compile on Overleaf).")
        sys.exit(2)
    res_texs = sorted(glob.glob(os.path.join(OUT, "Resumes", "*", "build-*.tex")))
    let_texs = sorted(glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.tex")))
    if "--approved" in sys.argv[1:]:
        res_ok, let_ok = approved_ids()
        if res_ok is None:
            print("note: --approved given but work/review.yaml has no items; building all. "
                  "Run: python engine/review.py")
            texs = res_texs + let_texs
        else:
            texs = [t for t in res_texs if folder_id(t) in res_ok] + \
                   [t for t in let_texs if folder_id(t) in let_ok]
            print("building APPROVED only: %d résumé id(s), %d letter id(s)" % (len(res_ok), len(let_ok)))
    else:
        texs = res_texs + let_texs
    fail = 0
    print(f"{'file':58} {'exit':4} {'pages'}")
    for t in texs:
        folder = os.path.dirname(t)
        r = subprocess.run([tec, os.path.basename(t)], cwd=folder, capture_output=True, text=True)
        pdf = t[:-4] + ".pdf"
        ok = (r.returncode == 0 and os.path.exists(pdf))
        if not ok: fail += 1
        rel = os.path.relpath(t, OUT)
        print(f"{rel:58} {r.returncode:<4} {pages(pdf) if os.path.exists(pdf) else '-'}")
    print(f"\nTOTAL={len(texs)}  FAIL={fail}")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()
