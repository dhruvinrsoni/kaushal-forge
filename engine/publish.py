#!/usr/bin/env python3
"""KaushalForge — publish chosen résumés to a static GitHub Pages hub.

Reads publish.yaml (labels + paths ONLY — never personal data) and:
  * copies ONLY the listed résumé PDFs into docs/resumes/,
  * writes docs/index.html (title, download links, footer on the page).

If the publish list is empty or a listed file is missing, it falls back to the in-repo
anonymized SAMPLE (docs/resumes/sample.pdf), clearly labeled as a PLACEHOLDER.

SAFETY: only .pdf files that live under output/Resumes/ may be published. Cover letters,
strategy docs, the knowledge base (work/), and raw inputs (inbox/) are never copied.

Run locally, then commit docs/index.html + docs/resumes/*.pdf. The .gitignore has a
scoped exception (!docs/resumes/*.pdf); everything else PDF stays ignored.
"""
import os, re, glob, shutil, html

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs"); RES_OUT = os.path.join(DOCS, "resumes")
RES_SRC_ROOT = os.path.join(ROOT, "output", "Resumes")
SAMPLE = "sample.pdf"

def load_cfg():
    import yaml
    p = os.path.join(ROOT, "publish.yaml")
    return (yaml.safe_load(open(p, encoding="utf-8")) or {}) if os.path.exists(p) else {}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "resume"

def is_safe_resume(path):
    """Allow ONLY a .pdf located under output/Resumes/ (never letters/strategy/work/inbox)."""
    ap = os.path.abspath(os.path.join(ROOT, path))
    if not ap.lower().endswith(".pdf"):
        return None, "not a .pdf"
    try:
        rel = os.path.relpath(ap, RES_SRC_ROOT)
    except ValueError:
        return None, "outside output/Resumes/"
    if rel.startswith("..") or os.path.isabs(rel):
        return None, "outside output/Resumes/ — only résumé PDFs may be published"
    return ap, None

def gather(cfg):
    chosen = []
    for it in (cfg.get("publish") or []):
        if not isinstance(it, dict):
            continue
        f, label = it.get("file"), it.get("label")
        if not f or not label:
            print(f"  skip (needs both file + label): {it}"); continue
        ap, why = is_safe_resume(f)
        if ap is None:
            print(f"  REJECT '{f}': {why}"); continue
        if not os.path.exists(ap):
            print(f"  skip (not generated yet): {f}"); continue
        chosen.append((label, ap))
    return chosen

def write_index(title, footer, entries, placeholder):
    rows = "\n".join(
        f'      <li><a href="resumes/{html.escape(fn)}">{html.escape(label)}</a></li>'
        for label, fn in entries
    ) or "      <li><em>No résumés published yet.</em></li>"
    note = (
        '<p class="note">These are anonymized <strong>placeholder</strong> samples. '
        'Edit <code>publish.yaml</code> and run <code>python engine/publish.py</code> '
        'to publish real résumés.</p>\n  ' if placeholder else ""
    )
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(title)}</title>
<style>
  :root {{ --bg:#0d1117; --card:#161b22; --ink:#e6edf3; --muted:#8b949e; --accent:#58a6ff; --border:#2a313c; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); }}
  main {{ max-width:720px; margin:0 auto; padding:48px 20px 96px; }}
  h1 {{ font-size:1.7rem; margin:0 0 16px; }}
  .note {{ background:var(--card); border:1px solid var(--border); border-left:3px solid var(--accent); padding:12px 16px; border-radius:8px; color:var(--muted); }}
  ul.resumes {{ list-style:none; padding:0; margin:28px 0; }}
  ul.resumes li {{ margin:0 0 12px; }}
  ul.resumes a {{ display:block; padding:16px 18px; background:var(--card); border:1px solid var(--border); border-radius:10px; color:var(--accent); text-decoration:none; font-weight:600; }}
  ul.resumes a:hover {{ border-color:var(--accent); }}
  footer {{ position:fixed; left:0; right:0; bottom:0; padding:12px 20px; text-align:center; font-size:.85rem; color:var(--muted); background:var(--bg); border-top:1px solid var(--border); }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(title)}</h1>
  {note}<ul class="resumes">
{rows}
  </ul>
</main>
<footer>{html.escape(footer)}</footer>
</body>
</html>
"""
    os.makedirs(DOCS, exist_ok=True)
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(doc)

def main():
    cfg = load_cfg()
    site = cfg.get("site") or {}
    title = site.get("title", "Résumés")
    footer = site.get("footer", "")
    os.makedirs(RES_OUT, exist_ok=True)
    # Idempotent: clear previously-published PDFs, keep the committed sample.
    for old in glob.glob(os.path.join(RES_OUT, "*.pdf")):
        if os.path.basename(old) != SAMPLE:
            os.remove(old)
    chosen = gather(cfg)
    entries, placeholder = [], False
    if chosen:
        for label, src in chosen:
            dest = slug(label) + ".pdf"
            shutil.copy2(src, os.path.join(RES_OUT, dest))
            entries.append((label, dest))
        print(f"Published {len(entries)} résumé(s) to docs/resumes/.")
    else:
        placeholder = True
        if os.path.exists(os.path.join(RES_OUT, SAMPLE)):
            entries.append(("Sample résumé — anonymized placeholder", SAMPLE))
        else:
            print("  WARN: docs/resumes/sample.pdf is missing; the hub will list nothing.")
        print("publish.yaml selects nothing -> showing the anonymized SAMPLE placeholder.")
        print("Edit publish.yaml's `publish:` list (résumé PDFs under output/Resumes/) and re-run.")
    write_index(title, footer, entries, placeholder)
    print(f"Wrote {os.path.join('docs', 'index.html')} ({len(entries)} entr{'y' if len(entries)==1 else 'ies'}).")

if __name__ == "__main__":
    main()
