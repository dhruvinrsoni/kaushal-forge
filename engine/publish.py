#!/usr/bin/env python3
"""KaushalForge — publish chosen résumés to a beautiful static GitHub Pages hub.

Workflow (all steps safe to re-run):

    python engine/publish.py --scan   # catalog every generated résumé into publish.yaml (publish: 0)
    # ...edit publish.yaml: flip `publish: 1` on the ones you want; set `live: 1` to go live...
    python engine/publish.py          # copy the publish:1 résumés into docs/resumes/ + build docs/index.html

Flags accept 1/0 or true/false (1/0 is shorter to scan). The top-level `live:` is a master
switch — set it to 0 to take EVERYTHING down at once (the hub falls back to the anonymized
SAMPLE), regardless of per-résumé flags.

The hub groups résumés by ROLE (one card each, a primary download + alternate formats), with
View / Download / Copy-link on every résumé and a Copy-site-link button — so a curated set
reads as a portfolio, not a file dump.

SAFETY: only .pdf files under output/Resumes/ are ever catalogued or published — never cover
letters, strategy docs, the knowledge base (work/), or raw inputs (inbox/).
"""
import os, re, sys, glob, shutil, html

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs"); RES_OUT = os.path.join(DOCS, "resumes")
LET_OUT = os.path.join(DOCS, "letters")
RES_SRC = os.path.join(ROOT, "output", "Resumes")
LET_SRC = os.path.join(ROOT, "output", "CoverLetters")
PUB_YAML = os.path.join(ROOT, "publish.yaml")
SAMPLE = "sample.pdf"
# The ONLY cover letter that may ever be published: the generic, company-agnostic master letter.
LETTER_SAMPLE_FILE = "output/CoverLetters/09-master-general/letter.pdf"
STYLE_NAMES = {"ats": "ATS", "modern": "Modern", "twocol": "Two-column"}
STYLE_FILE = {"ats": "ATS", "modern": "Modern", "twocol": "TwoCol"}  # filename-friendly
PLACEHOLDERS = ("%fill%", "your full name", "yourname")             # an unset config name
ACRONYMS = {"Ai": "AI", "Genai": "GenAI", "Ml": "ML", "Llm": "LLM", "Devops": "DevOps",
            "Devtools": "DevTools", "Sre": "SRE", "Mts": "MTS", "Api": "API", "Ui": "UI",
            "Ux": "UX", "Ci": "CI", "Cd": "CD", "Qa": "QA"}

HEADER = """\
# KaushalForge — publish switchboard. LABELS & PATHS ONLY; never put personal data here.
#
# 1. Generate résumés, then catalog them:   python engine/publish.py --scan
# 2. Flip `publish: 1` on the ones to make public (1/0 or true/false both work).
# 3. Set `live: 1` when you're ready to go public (live: 0 takes ALL résumés down at once).
# 4. Build + copy them into docs/:           python engine/publish.py
# 5. Commit publish.yaml + docs/index.html + docs/resumes/*.pdf, then push.
#
# Only résumé PDFs under output/Resumes/ can be published. Tip: publish ONE primary format
# per role (a focused set reads as a portfolio; a 60-PDF buffet reads as spray-and-pray).
# Nothing live/flagged (or an empty list) shows the anonymized SAMPLE placeholder.
#
# letter_sample: 1 additionally publishes the ONE generic master cover letter (09-master-general)
# as a writing sample -> docs/letters/. Per-company cover letters are NEVER publishable."""

def to_bool(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v.strip().lower() in ("1", "true", "yes", "on", "y")
    return False

def load():
    import yaml
    return (yaml.safe_load(open(PUB_YAML, encoding="utf-8")) or {}) if os.path.exists(PUB_YAML) else {}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "resume"

def fileslug(s):
    """Hyphenate but PRESERVE case (so 'AI GenAI Engineer' -> 'AI-GenAI-Engineer')."""
    return re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-")

_NAME_CACHE = []
def person_name():
    """config.person.name, or '' if unset/placeholder (then we fall back to role-only names)."""
    if not _NAME_CACHE:
        try:
            from kf_lib import load_cfg
            n = str(((load_cfg().get("person") or {}).get("name") or "")).strip()
            _NAME_CACHE.append("" if (not n or any(b in n.lower() for b in PLACEHOLDERS)) else n)
        except Exception:
            _NAME_CACHE.append("")
    return _NAME_CACHE[0]

def safe_resume(path):
    """abs path iff `path` is a .pdf under output/Resumes/, else None."""
    ap = os.path.abspath(os.path.join(ROOT, path))
    if not ap.lower().endswith(".pdf"):
        return None
    rel = os.path.relpath(ap, RES_SRC)
    return None if (rel.startswith("..") or os.path.isabs(rel)) else ap

def safe_letter_sample(path):
    """abs path iff `path` is the ONE generic, company-agnostic master letter PDF.
    Deliberately strict + separate from safe_resume: per-company letters are NEVER publishable.
    Accepts only output/CoverLetters/*-general/letter.pdf (the generic master letter)."""
    ap = os.path.abspath(os.path.join(ROOT, path))
    if not ap.lower().endswith("letter.pdf"):
        return None
    rel = os.path.relpath(ap, LET_SRC)
    if rel.startswith("..") or os.path.isabs(rel):
        return None
    folder = rel.replace("\\", "/").split("/")[0]
    return ap if folder.endswith("-general") else None

def derive(file):
    """Role title, role key, format label, stable dest filename, is_ats — from the path."""
    parts = file.replace("\\", "/").split("/")
    folder = parts[-2] if len(parts) >= 2 else "resume"
    base = re.sub(r"^\d+-", "", folder)                      # drop "01-"
    twopage = base.endswith("-2page")
    role_key = base[:-6] if twopage else base
    role_title = " ".join(ACRONYMS.get(w, w) for w in role_key.replace("-", " ").title().split())
    m = re.search(r"build-([a-z0-9]+)\.pdf$", file)
    sty = m.group(1) if m else "x"
    fmt = f"{STYLE_NAMES.get(sty, sty.upper())} · {'2-page' if twopage else '1-page'}"
    # Recruiter-friendly, unique filename: Full-Name-Resume-Role[-2page]-Style.pdf
    # Falls back to role-only (legacy) when the config name is unset/placeholder.
    style_file = STYLE_FILE.get(sty, sty.upper())
    core = f"{fileslug(role_title)}{'-2page' if twopage else ''}-{style_file}"
    name = fileslug(person_name())
    dest = f"{name}-Resume-{core}.pdf" if name else f"{slug(base)}-{sty}.pdf"
    return role_title, role_key, fmt, dest, sty == "ats"

def auto_label(file):
    role_title, _, fmt, _, _ = derive(file)
    return f"{role_title} ({fmt})"

def yq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

def emit_yaml(cfg, resumes):
    site = cfg.get("site") or {}
    out = [HEADER, "", f"live: {1 if to_bool(cfg.get('live', True)) else 0}"
           "   # master switch: 0 takes ALL résumés down (shows the sample); 1 = publish flagged ones",
           "", "site:",
           f"  title: {yq(site.get('title', 'Résumés'))}"]
    if site.get("subtitle"):
        out.append(f"  subtitle: {yq(site['subtitle'])}")
    out += [f"  footer: {yq(site.get('footer', ''))}",
            f"  discoverable: {1 if to_bool(site.get('discoverable', False)) else 0}"
            "   # 0 = noindex (share by link only); 1 = allow search engines",
            f"  ai_disclaimer: {1 if to_bool(site.get('ai_disclaimer', False)) else 0}"
            "   # 1 = show a small 'AI-assisted, reviewed by the candidate' note on the hub (default 0/off)",
            "",
            f"letter_sample: {1 if to_bool(cfg.get('letter_sample', False)) else 0}"
            "   # 1 = also publish the ONE generic master cover letter as a writing sample (per-company letters NEVER)",
            "", "resumes:"]
    if not resumes:
        out.append("  []   # run `python engine/publish.py --scan` after generating to auto-fill this")
    for r in resumes:
        out.append("  - { publish: %s, label: %s, file: %s }"
                   % (1 if to_bool(r.get("publish")) else 0, yq(r["label"]), r["file"]))
    open(PUB_YAML, "w", encoding="utf-8").write("\n".join(out) + "\n")

def scan(cfg):
    merged, seen = [], set()
    for r in (cfg.get("resumes") or []):
        if isinstance(r, dict) and r.get("file"):
            f = r["file"].replace("\\", "/")
            merged.append({"publish": to_bool(r.get("publish")), "label": r.get("label") or auto_label(f), "file": f})
            seen.add(f)
    new = 0
    for f in sorted(glob.glob(os.path.join(RES_SRC, "*", "build-*.pdf"))):
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        if rel in seen:
            continue
        merged.append({"publish": False, "label": auto_label(rel), "file": rel}); seen.add(rel); new += 1
    emit_yaml(cfg, merged)
    print(f"Cataloged {len(merged)} résumé(s) in publish.yaml ({new} new). "
          "Flip `publish: 1` on the ones to publish, set `live: 1`, then run: python engine/publish.py")

def linkify(text):
    esc = html.escape(text)
    def repl(m):
        tok = m.group(0); href = tok if tok.startswith("http") else "https://" + tok
        return f'<a href="{href}" target="_blank" rel="noopener">{tok}</a>'
    return re.sub(r"(https?://[^\s<]+|(?:www\.|github\.com/)[^\s<]+)", repl, esc)

def actions_html(dest):
    return (f'<span class="actions">'
            f'<a class="act" href="resumes/{html.escape(dest)}" target="_blank" rel="noopener" title="Open in browser">View</a>'
            f'<a class="act" href="resumes/{html.escape(dest)}" download title="Download the PDF">Download</a>'
            f'<button class="act copy" type="button" data-href="resumes/{html.escape(dest)}" title="Copy a direct link">Copy link</button>'
            f'</span>')

def card_html(role_title, items):
    primary = items[0]
    alts = items[1:]
    h = [f'  <article class="card">',
         f'    <h2>{html.escape(role_title)}</h2>',
         f'    <div class="primary"><span class="fmt">{html.escape(primary["fmt"])}</span>{actions_html(primary["dest"])}</div>']
    if alts:
        h.append('    <details class="alts"><summary>Other formats</summary>')
        for a in alts:
            h.append(f'      <div class="alt"><span class="fmt">{html.escape(a["fmt"])}</span>{actions_html(a["dest"])}</div>')
        h.append('    </details>')
    h.append('  </article>')
    return "\n".join(h)

def write_index(cfg, groups, placeholder, letter=None):
    site = cfg.get("site") or {}
    title = site.get("title", "Résumés")
    subtitle = site.get("subtitle", "")
    footer = site.get("footer", "")
    discoverable = to_bool(site.get("discoverable", False))
    ai_note = ('<div class="ai">Generated with AI assistance; reviewed by the candidate.</div>'
               if to_bool(site.get("ai_disclaimer", False)) else "")
    cards = "\n".join(card_html(rt, items) for rt, items in groups) or \
        '  <article class="card"><h2>No résumés published yet</h2></article>'
    note = ('<p class="note">Anonymized <strong>placeholder</strong>. Catalog with '
            '<code>publish.py --scan</code>, flip <code>publish: 1</code> (and <code>live: 1</code>) '
            'in <code>publish.yaml</code>, then re-run <code>publish.py</code>.</p>' if placeholder else "")
    robots = "" if discoverable else '\n<meta name="robots" content="noindex">'
    sub = f'\n  <p class="subtitle">{html.escape(subtitle)}</p>' if subtitle else ""
    letter_html = ("" if not letter else
                   '\n  <section class="letter"><h2>Cover letter (sample)</h2>'
                   '<p class="fmt">A generic, company-agnostic writing sample.</p>'
                   + actions_html(letter["dest"]).replace("resumes/", "letters/") + "</section>")
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">{robots}
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(subtitle or 'Résumé hub')}">
<meta property="og:type" content="website">
<title>{html.escape(title)}</title>
<script>(function(){{try{{var t=localStorage.getItem('kf-theme');if(t&&t!=='auto')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
<style>
  /* Light tokens (default + forced light) */
  :root, :root[data-theme="light"] {{ color-scheme:light; --bg:#ffffff; --elev:#f6f8fa; --card:#ffffff; --ink:#1f2328; --muted:#59636e; --accent:#0969da; --border:#d0d7de; }}
  /* Auto-dark: OS is dark and the user hasn't forced light */
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{ color-scheme:dark; --bg:#0d1117; --elev:#11161d; --card:#161b22; --ink:#e6edf3; --muted:#8b949e; --accent:#58a6ff; --border:#2a313c; }}
  }}
  /* Forced dark */
  :root[data-theme="dark"] {{ color-scheme:dark; --bg:#0d1117; --elev:#11161d; --card:#161b22; --ink:#e6edf3; --muted:#8b949e; --accent:#58a6ff; --border:#2a313c; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:16px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); }}
  header.hero {{ padding:56px 20px 8px; max-width:860px; margin:0 auto; }}
  header.hero h1 {{ font-size:2rem; margin:0; letter-spacing:-.01em; }}
  .subtitle {{ color:var(--muted); margin:6px 0 0; font-size:1.05rem; }}
  .toolbar {{ margin:18px 0 0; }}
  main {{ max-width:860px; margin:0 auto; padding:20px 20px 110px; }}
  .note {{ background:var(--elev); border:1px solid var(--border); border-left:3px solid var(--accent); padding:12px 16px; border-radius:8px; color:var(--muted); margin:0 0 22px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:16px; }}
  .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:18px 18px 14px; }}
  .card h2 {{ font-size:1.15rem; margin:0 0 12px; }}
  .fmt {{ color:var(--muted); font-size:.9rem; min-width:128px; }}
  .primary {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
  .actions {{ display:inline-flex; gap:6px; margin-left:auto; flex-wrap:wrap; }}
  .act {{ font:600 .82rem/1 inherit; padding:7px 11px; border-radius:8px; border:1px solid var(--border); background:var(--elev); color:var(--accent); text-decoration:none; cursor:pointer; }}
  .act:hover {{ border-color:var(--accent); }}
  details.alts {{ margin-top:12px; border-top:1px dashed var(--border); padding-top:8px; }}
  details.alts summary {{ cursor:pointer; color:var(--muted); font-size:.85rem; }}
  .alt {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-top:10px; }}
  .letter {{ margin-top:22px; background:var(--card); border:1px solid var(--border); border-radius:12px; padding:18px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
  .letter h2 {{ font-size:1.05rem; margin:0; }} .letter .actions {{ margin-left:auto; }}
  footer {{ position:fixed; left:0; right:0; bottom:0; padding:12px 20px; text-align:center; font-size:.82rem; color:var(--muted); background:var(--bg); border-top:1px solid var(--border); }}
  footer a {{ color:var(--accent); }}
  footer .ai {{ font-size:.78rem; opacity:.85; margin-bottom:3px; }}
  #toast {{ position:fixed; left:50%; bottom:64px; transform:translateX(-50%) translateY(20px); opacity:0; transition:.2s; background:var(--ink); color:var(--bg); font-weight:700; padding:9px 16px; border-radius:999px; pointer-events:none; }}
  #toast.show {{ opacity:1; transform:translateX(-50%) translateY(0); }}
</style>
</head>
<body>
<header class="hero">
  <h1>{html.escape(title)}</h1>{sub}
  <div class="toolbar"><button class="act" id="theme-toggle" type="button" title="Switch theme: auto / light / dark">◐ Auto</button> <button class="act copy" type="button" data-href="" title="Copy this page's link">Copy site link</button></div>
</header>
<main>
  {note}<div class="grid">
{cards}
  </div>{letter_html}
</main>
<footer>{ai_note}{linkify(footer)}</footer>
<div id="toast">Copied!</div>
<script>
  var toast = document.getElementById('toast'), t;
  function flash() {{ toast.classList.add('show'); clearTimeout(t); t = setTimeout(function(){{ toast.classList.remove('show'); }}, 1400); }}
  document.querySelectorAll('.copy').forEach(function(b) {{
    b.addEventListener('click', function() {{
      var rel = b.getAttribute('data-href');
      var url = rel ? new URL(rel, location.href).href : location.href;
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(flash, function() {{
        var i = document.createElement('input'); i.value = url; document.body.appendChild(i); i.select();
        try {{ document.execCommand('copy'); flash(); }} catch (e) {{}} document.body.removeChild(i);
      }});
    }});
  }});
  var root = document.documentElement, tbtn = document.getElementById('theme-toggle'), modes = ['auto','light','dark'], icons = {{ auto:'◐ Auto', light:'☀ Light', dark:'☾ Dark' }};
  function applyTheme(m) {{ if (m === 'auto') root.removeAttribute('data-theme'); else root.setAttribute('data-theme', m); try {{ localStorage.setItem('kf-theme', m); }} catch (e) {{}} if (tbtn) tbtn.textContent = icons[m]; }}
  var cur = 'auto'; try {{ cur = localStorage.getItem('kf-theme') || 'auto'; }} catch (e) {{}}
  applyTheme(modes.indexOf(cur) >= 0 ? cur : 'auto');
  if (tbtn) tbtn.addEventListener('click', function() {{ cur = modes[(modes.indexOf(cur) + 1) % modes.length]; applyTheme(cur); }});
</script>
</body>
</html>
"""
    os.makedirs(DOCS, exist_ok=True)
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(doc)

def publish(cfg):
    # GATE: publishing is the "goes public" boundary -> require an explicit human review sign-off
    # whenever real content would go live (flagged résumés or the letter sample). The sample/empty
    # placeholder path needs no review. No --yes bypass here on purpose: publishing a real person.
    wants_real = to_bool(cfg.get("live", True)) and (
        any(isinstance(r, dict) and to_bool(r.get("publish")) for r in (cfg.get("resumes") or []))
        or to_bool(cfg.get("letter_sample", False)))
    if wants_real:
        try:
            from kf_lib import review_state
            exists, ok = review_state()
        except Exception:
            exists, ok = (False, False)
        if not ok:
            print("BLOCKED: cannot publish a real person's résumés without a review sign-off.")
            if not exists:
                print("  Run: python engine/review.py   (then read work/REVIEW.md)")
            print("  Set `reviewed: 1` in work/review.yaml after reviewing, then re-run publish.")
            sys.exit(3)
    os.makedirs(RES_OUT, exist_ok=True)
    for old in glob.glob(os.path.join(RES_OUT, "*.pdf")):       # idempotent: drop prior published, keep sample
        if os.path.basename(old) != SAMPLE:
            os.remove(old)
    live = to_bool(cfg.get("live", True))
    published = []
    if live:
        for r in (cfg.get("resumes") or []):
            if not (isinstance(r, dict) and to_bool(r.get("publish"))):
                continue
            ap = safe_resume(r.get("file") or "")
            if ap is None:
                print(f"  REJECT (only résumé PDFs under output/Resumes/): {r.get('file')}"); continue
            if not os.path.exists(ap):
                print(f"  skip (not generated in this checkout): {r.get('file')}"); continue
            role_title, role_key, fmt, dest, _ = derive(r["file"])
            shutil.copy2(ap, os.path.join(RES_OUT, dest))
            published.append({"role_title": role_title, "role_key": role_key, "fmt": fmt, "dest": dest})
    # group by role (preserve first-seen order)
    groups, idx = [], {}
    for p in published:
        if p["role_key"] not in idx:
            idx[p["role_key"]] = len(groups); groups.append((p["role_title"], []))
        groups[idx[p["role_key"]]][1].append(p)
    placeholder = not groups
    if placeholder:
        if not live:
            print("Master switch OFF (live: 0) — all résumés taken down; showing the SAMPLE placeholder.")
        else:
            print("Nothing flagged `publish: 1` (or files missing) — showing the SAMPLE placeholder.")
        if os.path.exists(os.path.join(RES_OUT, SAMPLE)):
            groups = [("Sample résumé", [{"fmt": "anonymized placeholder", "dest": SAMPLE}])]
    else:
        n = sum(len(items) for _, items in groups)
        print(f"Published {n} résumé(s) across {len(groups)} role(s) to docs/resumes/.")

    # Opt-in: publish ONE generic, company-agnostic cover letter as a writing sample.
    # Strictly additive and separate from the résumé whitelist — per-company letters are never published.
    letter = None
    for old in glob.glob(os.path.join(LET_OUT, "*.pdf")):
        os.remove(old)
    if live and to_bool(cfg.get("letter_sample", False)):
        ap = safe_letter_sample(LETTER_SAMPLE_FILE)
        if ap is None:
            print("  REJECT letter_sample (only the generic *-general master letter may be published).")
        elif not os.path.exists(ap):
            print("  letter_sample on but the generic letter isn't built yet — skipping. "
                  "Run render_coverletters.py + build_pdfs.py.")
        else:
            name = fileslug(person_name())
            dest = f"{name}-Cover-Letter-Sample.pdf" if name else "cover-letter-sample.pdf"
            os.makedirs(LET_OUT, exist_ok=True)
            shutil.copy2(ap, os.path.join(LET_OUT, dest))
            letter = {"dest": dest}
            print(f"Published the generic cover-letter sample to docs/letters/{dest}.")

    write_index(cfg, groups, placeholder, letter)
    print("Wrote docs/index.html.")
    print("Next: \ngit add publish.yaml docs && git commit -m \"publish: update résumé hub\" && git push")

def main():
    cfg = load()
    if "--scan" in sys.argv[1:]:
        scan(cfg)
    else:
        publish(cfg)

if __name__ == "__main__":
    main()
