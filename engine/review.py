#!/usr/bin/env python3
"""KaushalForge — human review/approval checkpoint between "AI wrote the JSON" and "ship the PDFs".

    python engine/render_resumes.py          # writes content.tex per variant
    python engine/review.py                  # -> work/review.yaml (approve flags) + work/REVIEW.md (read it)
    # ...read work/REVIEW.md, fix any work/*.json, flip `approve: 0` on variants you DON'T want...
    python engine/build_pdfs.py --approved   # builds ONLY approved ids (default, no flag = build all)

Switchboard mirrors publish.yaml: re-running review.py refreshes the catalog but PRESERVES your
flips. Default approve = 1 when validation+hygiene pass for that file, 0 when they fail (nothing
broken ships by default). Page-2 fill is shown when output/fill-report.json exists (after a build).
This NEVER blocks and never edits content — it is a checkpoint for a human."""
import os, sys, json, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))          # engine/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
from kf_lib import ROOT, WORK, OUT, load_cfg, get_mask

REVIEW_YAML = os.path.join(WORK, "review.yaml")
REVIEW_MD = os.path.join(WORK, "REVIEW.md")

HEADER = """\
# KaushalForge review switchboard. Flip `approve: 0` on anything you DON'T want built/shipped.
# Then build only the approved set:  python engine/build_pdfs.py --approved
# (No flag = build all.) Re-running review.py refreshes this list but keeps your flips.
# Read work/REVIEW.md alongside this for headlines, validation status, and page-2 fill."""

def to_bool(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v.strip().lower() in ("1", "true", "yes", "on", "y")
    return False

def yq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

def load_array(path, wrappers=("results", "variants", "letters")):
    if not os.path.exists(path):
        return []
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    if isinstance(d, dict):
        for w in wrappers:
            if isinstance(d.get(w), list):
                return d[w]
        return []
    return d if isinstance(d, list) else []

def title_of(key):
    return " ".join(w for w in str(key).replace("-", " ").split()).title() or key

def fill_summary():
    """{id: 'ats 24% modern 24% twocol 17%'} from output/fill-report.json, if present."""
    fp = os.path.join(OUT, "fill-report.json")
    if not os.path.exists(fp):
        return {}
    try:
        data = json.load(open(fp, encoding="utf-8")).get("page2_fill", {})
    except Exception:
        return {}
    by_id = {}
    for rel, frac in data.items():
        parts = rel.split("/")
        if len(parts) < 2:
            continue
        folder = parts[-2]
        vid = folder.split("-", 1)[0]
        sty = parts[-1].replace("build-", "").replace(".pdf", "")
        by_id.setdefault(vid, []).append("%s %.0f%%" % (sty, frac * 100))
    return {k: " ".join(sorted(v)) for k, v in by_id.items()}

def existing_flips(items_key):
    """{id: approve_bool} from a prior review.yaml so re-scan keeps your choices."""
    try:
        import yaml
        prev = yaml.safe_load(open(REVIEW_YAML, encoding="utf-8")) or {}
    except Exception:
        return {}
    out = {}
    for r in (prev.get(items_key) or []):
        if isinstance(r, dict) and r.get("id") is not None:
            out[str(r["id"])] = to_bool(r.get("approve"))
    return out

def build():
    cfg = load_cfg()
    mask = get_mask(cfg)
    from validate import validate_file
    from rulecheck import check_file

    def file_status(path):
        """(schema_ok, schema_errs, hygiene_warns). Default-approve gates on SCHEMA only;
        hygiene (non-ASCII, GPA, ...) is advisory so one em-dash doesn't nuke the batch."""
        if not os.path.exists(path):
            return None, [], []
        serrs = validate_file(path)
        herrs = check_file(path, mask)
        return (not serrs), serrs, herrs

    variants = load_array(os.path.join(WORK, "variants.json"))
    letters = load_array(os.path.join(WORK, "letters.json"))
    fills = fill_summary()
    v_ok, v_errs, v_warn = file_status(os.path.join(WORK, "variants.json"))
    l_ok, l_errs, l_warn = file_status(os.path.join(WORK, "letters.json"))
    prev_r = existing_flips("resumes")
    prev_l = existing_flips("letters")

    # résumé rows (variants + the always-built Master id 09)
    res_rows = []
    for v in variants:
        vid = str(v.get("id", "")).strip()
        if not vid or vid == "09":
            continue
        res_rows.append({"id": vid, "label": title_of(v.get("key", vid)),
                         "headline": v.get("headline", ""), "fill": fills.get(vid, "")})
    res_rows.append({"id": "09", "label": "Master (all content)", "headline": "", "fill": fills.get("09", "")})
    res_rows.sort(key=lambda r: r["id"])

    let_rows = [{"id": str(x.get("id", "")).strip(), "label": title_of(x.get("key", x.get("id", "")))}
                for x in letters if str(x.get("id", "")).strip()]

    def approve_default(vid, prev, file_ok):
        if vid in prev:
            return prev[vid]
        return bool(file_ok)

    # write review.yaml
    lines = [HEADER, "", "resumes:"]
    for r in res_rows:
        ap = approve_default(r["id"], prev_r, v_ok)
        lines.append("  - { approve: %d, id: %s, label: %s }" % (1 if ap else 0, yq(r["id"]), yq(r["label"])))
    lines += ["", "letters:"]
    if not let_rows:
        lines.append("  []")
    for r in let_rows:
        ap = approve_default(r["id"], prev_l, l_ok)
        lines.append("  - { approve: %d, id: %s, label: %s }" % (1 if ap else 0, yq(r["id"]), yq(r["label"])))
    os.makedirs(WORK, exist_ok=True)
    open(REVIEW_YAML, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    # write REVIEW.md
    def vstat(ok, errs):
        if ok is None:
            return "(not present)"
        return "OK" if ok else "**%d schema error(s)** — these default to approve: 0" % len(errs)
    md = ["# Review — KaushalForge", "",
          "Edit `work/*.json` to fix anything below, then flip `approve` in `work/review.yaml`.",
          "Build only what you approved: `python engine/build_pdfs.py --approved`.", "",
          "## Schema (blocking — drives the default approve flag)", "",
          "- variants.json: " + vstat(v_ok, v_errs),
          "- letters.json: " + vstat(l_ok, l_errs)]
    if v_errs or l_errs:
        md += ["", "<details><summary>Schema errors</summary>", ""] + \
              ["- `%s`" % e for e in (v_errs + l_errs)] + ["", "</details>"]
    if v_warn or l_warn:
        md += ["", "## Hygiene (advisory — non-ASCII / GPA / entities; does NOT block)", "",
               "<details><summary>%d advisory note(s)</summary>" % (len(v_warn) + len(l_warn)), ""] + \
              ["- `%s`" % w for w in (v_warn + l_warn)] + ["", "</details>"]
    md += ["", "## Résumés", "", "| approve | id | role | page-2 fill | headline |",
           "|:--:|:--:|---|---|---|"]
    for r in res_rows:
        ap = approve_default(r["id"], prev_r, v_ok)
        hl = (r["headline"][:60] + "...") if len(r["headline"]) > 60 else r["headline"]
        md.append("| %s | %s | %s | %s | %s |" % ("1" if ap else "0", r["id"], r["label"], r["fill"] or "-", hl or "-"))
    if let_rows:
        md += ["", "## Cover letters", "", "| approve | id | company/role |", "|:--:|:--:|---|"]
        for r in let_rows:
            ap = approve_default(r["id"], prev_l, l_ok)
            md.append("| %s | %s | %s |" % ("1" if ap else "0", r["id"], r["label"]))
    if not fills:
        md += ["", "_Page-2 fill is blank until you build once (`build_pdfs.py` then `verify.py`)._"]
    open(REVIEW_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")

    print("Wrote work/review.yaml (%d résumé id(s), %d letter id(s)) and work/REVIEW.md."
          % (len(res_rows), len(let_rows)))
    blocked = (v_ok is False) or (l_ok is False)
    if blocked:
        print("NOTE: schema errors found — see work/REVIEW.md; affected files default to approve: 0.")
    if v_warn or l_warn:
        print("NOTE: %d hygiene advisory(ies) (non-ASCII etc.) — listed in REVIEW.md, non-blocking."
              % (len(v_warn) + len(l_warn)))
    print("Read work/REVIEW.md, flip approve in work/review.yaml, then: python engine/build_pdfs.py --approved")

if __name__ == "__main__":
    build()
