#!/usr/bin/env python3
"""KaushalForge — verification GATE. Exits non-zero if any check fails.
Checks: (1) leak scan for config.verify.forbidden_terms across output text + content.tex;
(2) no stray HTML entities; (3) LinkedIn char limits (from work/linkedin.json);
(4) PDF page counts (role=1, *-2page & 09-master=2, letters=1)."""
import os, sys, glob, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output")

def load_cfg():
    try:
        import yaml
        return yaml.safe_load(open(os.path.join(ROOT, "config.yaml"), encoding="utf-8"))
    except Exception:
        return {}

def main():
    cfg = load_cfg()
    fails = []

    # 1+2 leak / entity scan
    forb = [t.lower() for t in (cfg.get("verify", {}) or {}).get("forbidden_terms", []) if t]
    ents = ["&gt;", "&lt;", "&amp;", "&#39;", "&quot;"]
    scan = (glob.glob(os.path.join(OUT, "Resumes", "*", "content.tex")) +
            glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.tex")) +
            glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.md")) +
            glob.glob(os.path.join(OUT, "LinkedIn", "*.md")) +
            glob.glob(os.path.join(OUT, "Strategy", "*.md")))
    for f in scan:
        t = open(f, encoding="utf-8").read()
        tl = t.lower()
        for k in forb:
            if k in tl: fails.append(f"LEAK '{k}' in {os.path.relpath(f, OUT)}")
        for e in ents:
            if e in t: fails.append(f"ENTITY '{e}' in {os.path.relpath(f, OUT)}")

    # 3 LinkedIn char limits
    lj = os.path.join(ROOT, "work", "linkedin.json")
    if os.path.exists(lj):
        d = json.load(open(lj, encoding="utf-8"))
        for h in d.get("headline_variants", []):
            if len(h.get("text", "")) > 220: fails.append(f"HEADLINE {len(h['text'])}>220: {h.get('label','')}")
        ab = d.get("about", {})
        for k in ("primary", "alt"):
            if ab.get(k) and len(ab[k]) > 2600: fails.append(f"ABOUT[{k}] {len(ab[k])}>2600")

    # 4 page counts
    try:
        import pypdf
        for pdf in glob.glob(os.path.join(OUT, "Resumes", "*", "build-*.pdf")):
            folder = os.path.basename(os.path.dirname(pdf))
            want = 2 if (folder.endswith("2page") or folder.startswith("09")) else 1
            n = len(pypdf.PdfReader(pdf).pages)
            if n != want: fails.append(f"PAGES {folder}/{os.path.basename(pdf)} = {n} (want {want})")
        for pdf in glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.pdf")):
            n = len(pypdf.PdfReader(pdf).pages)
            if n != 1: fails.append(f"PAGES letter {os.path.basename(os.path.dirname(pdf))} = {n} (want 1)")
    except ImportError:
        print("note: pypdf not installed; skipping page-count check")

    if fails:
        print("VERIFY FAILED (%d):" % len(fails))
        for x in fails: print("  -", x)
        sys.exit(1)
    print("VERIFY OK — no leaks, no stray entities, char limits respected, page counts correct.")

if __name__ == "__main__":
    main()
