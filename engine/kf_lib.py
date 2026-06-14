#!/usr/bin/env python3
"""KaushalForge — shared deterministic primitives (paths, config, mask, limits).
Imported by verify.py and the engine/tools/* guardrails so leak/limit logic lives
in exactly one place. No intelligence here; identical on any machine."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))          # engine/
ROOT = os.path.dirname(HERE)                               # repo root
OUT = os.path.join(ROOT, "output")
WORK = os.path.join(ROOT, "work")
SCHEMAS = os.path.join(ROOT, ".github", "skills", "kaushal-forge", "schemas")

SRC_EXTS = (".md", ".tex", ".json", ".yaml", ".yml", ".py", ".txt", ".html", ".toml", ".cfg", ".ini")
CONFIG_FILES = ("config.yaml", "config.example.yaml")      # the mask/term list legitimately lives here
ENTITIES = ("&gt;", "&lt;", "&amp;", "&#39;", "&quot;")
LINKEDIN_LIMITS = {"headline": 220, "about": 2600}
REVIEW_YAML = os.path.join(WORK, "review.yaml")

# AI-generated disclaimer (ASCII, leak-free). Operator/repo-facing only; never printed on the
# resume/letter PDFs. One source of truth, imported by every renderer.
_DISCLAIMER_BODY = ("NOT verified fact. A human must review, correct, and own every claim "
                    "before it is sent, published, or relied upon.")
AI_DISCLAIMER = "AI-assisted draft (KaushalForge): " + _DISCLAIMER_BODY
AI_DISCLAIMER_MD = "> **AI-assisted draft.** " + _DISCLAIMER_BODY + "\n"

def to_bool(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v.strip().lower() in ("1", "true", "yes", "on", "y")
    return False

def review_state():
    """(exists, approved) for work/review.yaml. approved == top-level `reviewed` flag is truthy.
    Missing file => (False, False): no review was generated (draft/CI context), so callers don't block."""
    if not os.path.exists(REVIEW_YAML):
        return (False, False)
    try:
        import yaml
        d = yaml.safe_load(open(REVIEW_YAML, encoding="utf-8")) or {}
    except Exception:
        return (True, False)
    return (True, to_bool(d.get("reviewed", 0)))

def load_cfg():
    """Parse config.yaml (repo root). {} if missing or PyYAML unavailable."""
    try:
        import yaml
        return yaml.safe_load(open(os.path.join(ROOT, "config.yaml"), encoding="utf-8")) or {}
    except Exception:
        return {}

def get_mask(cfg):
    """{lowercased term: replacement} from verify.mask (dict) + legacy verify.forbidden_terms (list)."""
    v = (cfg or {}).get("verify", {}) or {}
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

def tracked_text_files():
    """Tracked, committable text files (so a sensitive term in a skill/doc is caught). None if not git."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    files = []
    for rel in out.splitlines():
        if os.path.basename(rel) in CONFIG_FILES:
            continue
        if rel.lower().endswith(SRC_EXTS):
            files.append(os.path.join(ROOT, rel))
    return files
