#!/usr/bin/env python3
"""KaushalForge — compile every résumé build-*.tex and cover-letter letter.tex with Tectonic.
Prints a pass/fail + page-count table. Exit non-zero if any compile fails."""
import os, sys, glob, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output")

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
    texs = sorted(glob.glob(os.path.join(OUT, "Resumes", "*", "build-*.tex")) +
                  glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.tex")))
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
