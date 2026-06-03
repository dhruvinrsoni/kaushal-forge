#!/usr/bin/env python3
"""KaushalForge — render LinkedIn section files from work/linkedin.json -> output/LinkedIn/*.md.
Tolerant: emits whatever sections are present. Adds live character counts (limits enforced by verify.py).
linkedin.json shape:
{ headline_variants:[{label,text}], about:{primary,alt}, experience:[{title,org,dates,location,bullets:[],skills_line}],
  skills:{ordered:[],pin3:[]}, featured:[{title,note}], certs_order:[], misc:[] }
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output", "LinkedIn")

def main():
    d = json.load(open(os.path.join(ROOT, "work", "linkedin.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    def w(name, text): open(os.path.join(OUT, name), "w", encoding="utf-8").write(text)

    w("00-overview.md", "# LinkedIn rewrite — paste-ready, with rationale\n\n"
      "Apply order: settings (07) → headline (01) → about (02) → experience (03) → skills (04) → featured (05) → certs/edu (06).\n"
      "Limits: Headline ≤220 · About ≤2600 · Experience ≤2000/role · Skills 50 (pin 3) · Title ≤100.\n")

    if d.get("headline_variants"):
        s = "# Headline (≤220 chars) — pick ONE\n\n"
        for h in d["headline_variants"]:
            s += f"### {h.get('label','Option')}  ·  {len(h['text'])} chars\n```\n{h['text']}\n```\n\n"
        w("01-headline.md", s)

    if d.get("about"):
        a = d["about"]; s = "# About (≤2600 chars)\n\n"
        if a.get("primary"): s += f"### Primary — {len(a['primary'])} chars\n```\n{a['primary']}\n```\n\n"
        if a.get("alt"):     s += f"### Shorter alt — {len(a['alt'])} chars\n```\n{a['alt']}\n```\n"
        w("02-about.md", s)

    if d.get("experience"):
        s = "# Experience — per-role descriptions (≤2000 chars each)\n\n"
        for e in d["experience"]:
            head = f"## {e.get('title','')} · {e.get('org','')} · {e.get('dates','')}"
            if e.get("location"): head += f" · {e['location']}"
            body = "\n".join("• " + b for b in e.get("bullets", []))
            if e.get("skills_line"): body += "\n\nSkills: " + e["skills_line"]
            s += f"{head}\n```\n{body}\n```\n\n"
        w("03-experience.md", s)

    if d.get("skills"):
        sk = d["skills"]; s = "# Skills (max 50; pin 3)\n\n"
        if sk.get("pin3"): s += "## Pin these 3\n" + "\n".join(f"{i+1}. **{x}**" for i, x in enumerate(sk["pin3"])) + "\n\n"
        if sk.get("ordered"): s += "## Keep, in priority order\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(sk["ordered"])) + "\n"
        w("04-skills.md", s)

    if d.get("featured"):
        s = "# Featured + Projects — lead with your best public work\n\n"
        for it in d["featured"]:
            s += f"- **{it.get('title','')}** — {it.get('note','')}\n"
        w("05-featured-and-projects.md", s)

    if d.get("certs_order"):
        s = "# Certifications · Education · Awards (ordering)\n\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(d["certs_order"])) + "\n"
        w("06-certs-education-awards.md", s)

    if d.get("misc"):
        s = "# Settings & misc — diplomatic discoverability\n\n" + "\n".join("- " + m for m in d["misc"]) + "\n"
        w("07-misc-settings.md", s)

    print("DONE render_linkedin")

if __name__ == "__main__":
    main()
