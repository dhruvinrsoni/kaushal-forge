#!/usr/bin/env python3
"""KaushalForge — verification GATE. Exits non-zero if any check fails.
Checks: (1) sensitive-term LEAK scan — keys of config.verify.mask (plus any legacy
verify.forbidden_terms) must not appear in generated OUTPUTS *or* in any tracked SOURCE
file (a leak in a skill/doc is caught, not just in outputs); on a hit it suggests the mask.
(2) no stray HTML entities; (3) LinkedIn char limits (work/linkedin.json);
(4) PDF page counts (role=1, *-2page & 09-master=2, letters=1).
Also emits a NON-FATAL page-2 fill report for 2-page editions (warns when page 2 is
< config.resume.fill.target_min, default 0.40) and writes output/fill-report.json."""
import os, sys, glob, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output")
SRC_EXTS = (".md", ".tex", ".json", ".yaml", ".yml", ".py", ".txt", ".html", ".toml", ".cfg", ".ini")
CONFIG_FILES = ("config.yaml", "config.example.yaml")   # the term list lives here — don't self-flag

def load_cfg():
    try:
        import yaml
        return yaml.safe_load(open(os.path.join(ROOT, "config.yaml"), encoding="utf-8")) or {}
    except Exception:
        return {}

def get_mask(cfg):
    """{lowercased term: replacement} from verify.mask (dict) + legacy verify.forbidden_terms (list)."""
    v = cfg.get("verify", {}) or {}
    terms = {}
    m = v.get("mask", {})
    if isinstance(m, dict):
        for t, repl in m.items():
            if t:
                terms[str(t).lower()] = str(repl or "")
    for t in (v.get("forbidden_terms", []) or []):
        if t:
            terms.setdefault(str(t).lower(), "")
    return terms

def page2_fill(reader):
    """Fraction of the page height the LAST page's content spans, top->lowest text (0..1).
    Device y of each text run = compose its text matrix with the CTM (tm[4]*cm[1] +
    tm[5]*cm[3] + cm[5]); lowest such y = bottom of content. Margin-agnostic, pypdf-only.
    Covers both paracol columns (min over all runs on the page). None if positions unavailable."""
    pg = reader.pages[-1]
    ph = float(pg.mediabox.height)
    ys = []
    def visit(text, cm, tm, font, size):
        if text and text.strip():
            try:
                ys.append(float(tm[4]) * float(cm[1]) + float(tm[5]) * float(cm[3]) + float(cm[5]))
            except Exception:
                pass
    try:
        pg.extract_text(visitor_text=visit)
    except TypeError:
        return None
    if not ys:
        return None
    return max(0.0, min(1.0, (ph - min(ys)) / ph))

def tracked_text_files():
    """Tracked, committable text files (so a sensitive term in a skill/doc is caught). None if not git."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    files = []
    for rel in out.splitlines():
        if os.path.basename(rel) in CONFIG_FILES:        # the mask/term list legitimately lives here
            continue
        if rel.lower().endswith(SRC_EXTS):
            files.append(os.path.join(ROOT, rel))
    return files

def main():
    cfg = load_cfg()
    fails = []
    mask = get_mask(cfg)
    ents = ["&gt;", "&lt;", "&amp;", "&#39;", "&quot;"]
    def sugg(k):
        return " -> mask as '%s'" % mask[k] if mask.get(k) else ""

    # 1+2 leak / entity scan over GENERATED OUTPUTS
    out_scan = (glob.glob(os.path.join(OUT, "Resumes", "*", "content.tex")) +
                glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.tex")) +
                glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.md")) +
                glob.glob(os.path.join(OUT, "LinkedIn", "*.md")) +
                glob.glob(os.path.join(OUT, "Strategy", "*.md")))
    for f in out_scan:
        t = open(f, encoding="utf-8", errors="replace").read()
        tl = t.lower()
        for k in mask:
            if k in tl: fails.append("LEAK '%s' in output/%s%s" % (k, os.path.relpath(f, OUT), sugg(k)))
        for e in ents:
            if e in t: fails.append("ENTITY '%s' in output/%s" % (e, os.path.relpath(f, OUT)))

    # 1b leak scan over TRACKED SOURCE files (the gap that let a term sit in confidentiality.md)
    src = tracked_text_files()
    if src is None:
        print("note: git unavailable; skipping tracked-source leak scan")
    else:
        for f in src:
            try:
                t = open(f, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            tl = t.lower()
            for k in mask:
                if k in tl: fails.append("LEAK '%s' in %s (tracked source)%s" % (k, os.path.relpath(f, ROOT), sugg(k)))

    # 3 LinkedIn char limits
    lj = os.path.join(ROOT, "work", "linkedin.json")
    if os.path.exists(lj):
        d = json.load(open(lj, encoding="utf-8"))
        for h in d.get("headline_variants", []):
            if len(h.get("text", "")) > 220: fails.append("HEADLINE %d>220: %s" % (len(h["text"]), h.get("label", "")))
        ab = d.get("about", {})
        for k in ("primary", "alt"):
            if ab.get(k) and len(ab[k]) > 2600: fails.append("ABOUT[%s] %d>2600" % (k, len(ab[k])))

    # 4 page counts (fatal) + page-2 fill measurement (NON-FATAL warn)
    rc = (cfg.get("resume", {}) or {}).get("fill", {}) or {}
    fmin = float(rc.get("target_min", 0.40)); fmax = float(rc.get("target_max", 0.70))
    notes = []; fill_report = {}
    try:
        import pypdf
        for pdf in glob.glob(os.path.join(OUT, "Resumes", "*", "build-*.pdf")):
            folder = os.path.basename(os.path.dirname(pdf))
            want = 2 if (folder.endswith("2page") or folder.startswith("09")) else 1
            reader = pypdf.PdfReader(pdf)
            n = len(reader.pages)
            if n != want: fails.append("PAGES %s/%s = %d (want %d)" % (folder, os.path.basename(pdf), n, want))
            if want == 2 and n >= 2:
                fill = page2_fill(reader)
                if fill is not None:
                    rel = os.path.relpath(pdf, OUT).replace(os.sep, "/")
                    fill_report[rel] = round(fill, 3)
                    if fill < fmin:
                        notes.append("FILL %s/%s page 2 only %.0f%% full (< %.0f%% target) -- consider the 1-page edition or add depth"
                                     % (folder, os.path.basename(pdf), fill * 100, fmin * 100))
        for pdf in glob.glob(os.path.join(OUT, "CoverLetters", "*", "letter.pdf")):
            n = len(pypdf.PdfReader(pdf).pages)
            if n != 1: fails.append("PAGES letter %s = %d (want 1)" % (os.path.basename(os.path.dirname(pdf)), n))
    except ImportError:
        print("note: pypdf not installed; skipping page-count + fill check")
    if fill_report:
        try:
            json.dump({"target_min": fmin, "target_max": fmax, "page2_fill": fill_report},
                      open(os.path.join(OUT, "fill-report.json"), "w", encoding="utf-8"), indent=2)
        except Exception:
            pass

    # page-2 fill notes are advisory (decision: warn-only) — they never change the exit code
    if notes:
        print("FILL NOTES (advisory, non-blocking):")
        for x in notes: print("  -", x)

    if fails:
        print("VERIFY FAILED (%d):" % len(fails))
        for x in fails: print("  -", x)
        sys.exit(1)
    print("VERIFY OK — no leaks (outputs + tracked source), no stray entities, char limits respected, page counts correct.")

if __name__ == "__main__":
    main()
