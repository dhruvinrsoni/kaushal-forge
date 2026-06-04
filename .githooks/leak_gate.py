#!/usr/bin/env python3
"""KaushalForge leak gate (logic) — invoked by .githooks/pre-commit.

Blocks any commit whose STAGED content (text or PDF visible-text) contains a sensitive term
from config.verify.mask (or legacy verify.forbidden_terms). The term list lives in the
gitignored config.yaml, so this runs locally. Bypass only if truly certain: git commit --no-verify.
"""
import subprocess, sys, os, io

def sh(*args):
    return subprocess.run(args, capture_output=True)

def root():
    return sh("git", "rev-parse", "--show-toplevel").stdout.decode("utf-8", "replace").strip()

def terms(ROOT):
    p = os.path.join(ROOT, "config.yaml")
    if not os.path.exists(p):
        return {}
    try:
        import yaml
    except Exception:
        print("KaushalForge gate: pyyaml missing; cannot read config.verify.mask — run engine/bootstrap.py")
        return {}
    cfg = yaml.safe_load(open(p, encoding="utf-8")) or {}
    v = cfg.get("verify", {}) or {}
    t = {}
    if isinstance(v.get("mask"), dict):
        for k, repl in v["mask"].items():
            if k: t[str(k).lower()] = str(repl or "")
    for k in (v.get("forbidden_terms", []) or []):
        if k: t.setdefault(str(k).lower(), "")
    return t

def staged_files():
    out = sh("git", "diff", "--cached", "--name-only", "--diff-filter=ACM").stdout.decode("utf-8", "replace")
    return [f for f in out.splitlines() if f]

def staged_text(path):
    blob = sh("git", "show", ":" + path).stdout            # staged version, bytes
    if path.lower().endswith(".pdf"):
        try:
            import pypdf
            return "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(io.BytesIO(blob)).pages)
        except Exception:
            return ""                                       # can't read -> can't scan; don't false-block
    try:
        return blob.decode("utf-8", "replace")
    except Exception:
        return ""

def main():
    ROOT = root()
    T = terms(ROOT)
    if not T:
        sys.exit(0)                                         # nothing configured to gate
    CONFIG = ("config.yaml", "config.example.yaml")          # term list legitimately lives here
    hits = []
    for f in staged_files():
        if os.path.basename(f) in CONFIG:
            continue
        tl = staged_text(f).lower()
        for k in T:
            if k in tl:
                hits.append((k, f, T[k]))
    if hits:
        print("KaushalForge pre-commit GATE: BLOCKED — sensitive term(s) in staged content:")
        for k, f, m in hits:
            print("  - '%s' in %s%s" % (k, f, (" -> mask as '%s'" % m) if m else ""))
        print("Fix the file (generalise per config.verify.mask) and re-stage. "
              "Override only if certain: git commit --no-verify.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
