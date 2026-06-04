#!/usr/bin/env python3
"""KaushalForge — publish chosen résumés to a static GitHub Pages hub.

Two steps, both safe to re-run:

    python engine/publish.py --scan   # catalog every generated résumé into publish.yaml (publish: false)
    # ...edit publish.yaml: flip `publish: true` on the ones you want public...
    python engine/publish.py          # copy the publish:true résumés into docs/resumes/ + build docs/index.html

If nothing is flagged true (or a flagged file is missing in this checkout), the hub shows
the in-repo anonymized SAMPLE (docs/resumes/sample.pdf) as a labeled placeholder.

SAFETY: only .pdf files under output/Resumes/ are ever catalogued or published — never cover
letters, strategy docs, the knowledge base (work/), or raw inputs (inbox/). Run locally, then
commit publish.yaml + docs/index.html + docs/resumes/*.pdf (the .gitignore allows docs/resumes/*.pdf).
"""
import os, re, sys, glob, shutil, html

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs"); RES_OUT = os.path.join(DOCS, "resumes")
RES_SRC = os.path.join(ROOT, "output", "Resumes")
PUB_YAML = os.path.join(ROOT, "publish.yaml")
SAMPLE = "sample.pdf"

HEADER = """\
# KaushalForge — publish switchboard. LABELS & PATHS ONLY; never put personal data here.
#
# 1. Generate résumés, then catalog them:   python engine/publish.py --scan
# 2. Flip `publish: true` on the ones to make public (edit the list below).
# 3. Build + copy them into docs/:           python engine/publish.py
# 4. Commit publish.yaml + docs/index.html + docs/resumes/*.pdf, then push.
#
# Only résumé PDFs under output/Resumes/ can be published. Nothing flagged true
# (or an empty list) shows the anonymized SAMPLE placeholder."""

def load():
    import yaml
    return (yaml.safe_load(open(PUB_YAML, encoding="utf-8")) or {}) if os.path.exists(PUB_YAML) else {}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "resume"

def safe_resume(path):
    """Return abs path iff `path` is a .pdf located under output/Resumes/, else None."""
    ap = os.path.abspath(os.path.join(ROOT, path))
    if not ap.lower().endswith(".pdf"):
        return None
    rel = os.path.relpath(ap, RES_SRC)
    return None if (rel.startswith("..") or os.path.isabs(rel)) else ap

def auto_label(rel_in_resumes):
    """'01-software-engineer-backend/build-ats.pdf' -> 'Software Engineer Backend (ATS)'."""
    folder = rel_in_resumes.replace("\\", "/").split("/", 1)[0]
    folder = re.sub(r"^\d+-", "", folder).replace("-", " ").strip().title()
    m = re.search(r"build-([a-z]+)\.pdf$", rel_in_resumes)
    return f"{folder} ({m.group(1).upper()})" if m else folder

def yq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

def emit_yaml(site, resumes):
    out = [HEADER, "", "site:",
           f"  title: {yq(site.get('title', 'Résumés'))}",
           f"  footer: {yq(site.get('footer', ''))}",
           "", "resumes:"]
    if not resumes:
        out.append("  []   # run `python engine/publish.py --scan` after generating to auto-fill this")
    for r in resumes:
        out.append("  - { publish: %s, label: %s, file: %s }"
                   % ("true" if r["publish"] else "false", yq(r["label"]), r["file"]))
    open(PUB_YAML, "w", encoding="utf-8").write("\n".join(out) + "\n")

def scan(cfg):
    site = cfg.get("site") or {}
    merged, seen = [], set()
    for r in (cfg.get("resumes") or []):              # keep existing entries (and their flags/labels)
        if isinstance(r, dict) and r.get("file"):
            f = r["file"].replace("\\", "/")
            merged.append({"publish": bool(r.get("publish")), "label": r.get("label") or "", "file": f})
            seen.add(f)
    found = sorted(glob.glob(os.path.join(RES_SRC, "*", "build-*.pdf")))
    new = 0
    for f in found:                                    # append newly-discovered résumés as publish: false
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        if rel in seen:
            continue
        relres = os.path.relpath(f, RES_SRC).replace("\\", "/")
        merged.append({"publish": False, "label": auto_label(relres), "file": rel})
        seen.add(rel); new += 1
    emit_yaml(site, merged)
    print(f"Cataloged {len(found)} résumé PDF(s) under output/Resumes/ "
          f"-> {len(merged)} entries in publish.yaml ({new} new).")
    print("Flip `publish: true` on the ones to make public, then run: python engine/publish.py")

def write_index(title, footer, entries, placeholder):
    rows = "\n".join(
        f'      <li><a href="resumes/{html.escape(fn)}">{html.escape(label)}</a></li>'
        for label, fn in entries
    ) or "      <li><em>No résumés published yet.</em></li>"
    note = ('<p class="note">These are anonymized <strong>placeholder</strong> samples. '
            'Catalog with <code>python engine/publish.py --scan</code>, flip '
            '<code>publish: true</code> in <code>publish.yaml</code>, then re-run '
            '<code>python engine/publish.py</code>.</p>\n  ' if placeholder else "")
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

def publish(cfg):
    site = cfg.get("site") or {}
    title, footer = site.get("title", "Résumés"), site.get("footer", "")
    os.makedirs(RES_OUT, exist_ok=True)
    for old in glob.glob(os.path.join(RES_OUT, "*.pdf")):      # idempotent: drop prior published, keep sample
        if os.path.basename(old) != SAMPLE:
            os.remove(old)
    entries, used = [], set()
    for r in (cfg.get("resumes") or []):
        if not (isinstance(r, dict) and r.get("publish")):
            continue
        f = r.get("file")
        ap = safe_resume(f) if f else None
        if ap is None:
            print(f"  REJECT (only résumé PDFs under output/Resumes/ may be published): {f}"); continue
        if not os.path.exists(ap):
            print(f"  skip (not generated in this checkout): {f}"); continue
        label = r.get("label") or auto_label(os.path.relpath(ap, RES_SRC))
        dest = slug(label) + ".pdf"
        n = 2
        while dest in used:
            dest = f"{slug(label)}-{n}.pdf"; n += 1
        used.add(dest)
        shutil.copy2(ap, os.path.join(RES_OUT, dest))
        entries.append((label, dest))
    placeholder = not entries
    if placeholder:
        if os.path.exists(os.path.join(RES_OUT, SAMPLE)):
            entries.append(("Sample résumé — anonymized placeholder", SAMPLE))
        print("Nothing flagged `publish: true` (or files missing) -> showing the SAMPLE placeholder.")
        print("Run `python engine/publish.py --scan`, flip a flag to true, then re-run.")
    else:
        print(f"Published {len(entries)} résumé(s) to docs/resumes/.")
    write_index(title, footer, entries, placeholder)
    print(f"Wrote docs/index.html ({len(entries)} entr{'y' if len(entries)==1 else 'ies'}).")

def main():
    cfg = load()
    if "--scan" in sys.argv[1:]:
        scan(cfg)
    else:
        publish(cfg)

if __name__ == "__main__":
    main()
