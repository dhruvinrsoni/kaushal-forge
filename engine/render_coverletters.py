#!/usr/bin/env python3
"""KaushalForge — render cover letters from config + work/letters.json (model-agnostic).
Output: output/CoverLetters/_styles/cf-letter.tex + <id>-<key>/{letter.tex,letter.md}.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STYLES_SRC = os.path.join(HERE, "templates", "styles")
OUT = os.path.join(ROOT, "output", "CoverLetters")

def load_config():
    import yaml
    return yaml.safe_load(open(os.path.join(ROOT, "config.yaml"), encoding="utf-8"))

def esc(s):
    s = str(s)
    s = s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
    s = s.replace('\\', r'\textbackslash{}')
    s = s.replace('&', r'\&').replace('%', r'\%').replace('#', r'\#').replace('_', r'\_')
    s = s.replace('$', r'\$')
    s = s.replace('->', r'$\rightarrow$')
    s = s.replace('~', r'\textasciitilde{}')
    out, openq = [], True
    for ch in s:
        if ch == '"':
            out.append('``' if openq else "''"); openq = not openq
        else:
            out.append(ch)
    return ''.join(out)

def deent(s):
    return (s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
             .replace('&#39;', "'").replace('&quot;', '"')) if isinstance(s, str) else s

def contact_line(cfg):
    c = cfg.get("contact", {}); parts = []
    if c.get("email"):    parts.append(r"\href{mailto:%s}{%s}" % (c["email"], c["email"]))
    if c.get("phone"):    parts.append(esc(c["phone"]))
    if c.get("linkedin"): parts.append(r"\href{https://%s}{%s}" % (c["linkedin"], c["linkedin"]))
    if c.get("github"):   parts.append(r"\href{https://%s}{%s}" % (c["github"], c["github"]))
    loc = cfg.get("person", {}).get("location_display", "")
    if loc: parts.append(esc(loc.split("|")[0].strip()))
    return r" \textbullet{} ".join(parts)

def copy_style(accent_hex):
    dst = os.path.join(OUT, "_styles"); os.makedirs(dst, exist_ok=True)
    txt = open(os.path.join(STYLES_SRC, "cf-letter.tex"), encoding="utf-8").read()
    if accent_hex:
        txt = re.sub(r"(\\definecolor\{accent\}\{HTML\}\{)[0-9A-Fa-f]{6}(\})", r"\g<1>%s\g<2>" % accent_hex, txt)
    open(os.path.join(dst, "cf-letter.tex"), "w", encoding="utf-8").write(txt)

def letter_tex(v, cfg):
    L = [r"% Cover letter -- compile with tectonic letter.tex (or Overleaf). FILL the [bracketed] bits.",
         r"\documentclass[letterpaper,11pt]{article}",
         r"\input{../_styles/cf-letter.tex}",
         r"\begin{document}",
         r"\Name{%s}" % esc(cfg["person"]["name"]),
         r"\Contact{%s}" % contact_line(cfg),
         r"\LetterDate{[Date]}",
         r"\Recipient{Hiring Team, [Company]\newline [City, Country]}",
         r"\Subject{Re: [Role] --- Application}",
         r"\Greeting{Dear [Hiring Manager],}",
         r"\LetterBody{%",
         r"\Para{%s}" % esc(v["opening"])]
    L += [r"\Para{%s}" % esc(p) for p in v["body"]]
    L += [r"\Fill{[Why [Company]: add 1--2 specific, researched sentences here, then delete this note --- see letter.md for a prompt.]}",
          r"\Para{%s}" % esc(v["closing"]),
          r"}", r"\Signoff{Sincerely,}", r"\BuildLetter", r"\end{document}"]
    return "\n".join(L) + "\n"

def letter_md(v, cfg):
    body = "\n\n".join(v["body"])
    return (f"**Subject:** {v['email_subject']}\n\n---\n\n[Date]\n\n"
            f"Hiring Team, [Company]  \n[City, Country]\n\nDear [Hiring Manager],\n\n"
            f"{v['opening']}\n\n{body}\n\n> {v['why_company_prompt']}\n\n{v['closing']}\n\n"
            f"Sincerely,  \n**{cfg['person']['name']}**  \n[email] · [phone] · "
            f"{cfg.get('contact',{}).get('linkedin','')}\n\n---\n\n"
            f"### Notes (delete before sending)\n{v['notes_md']}\n\n"
            f"**Fill before sending:** [Company], [Role], [Hiring Manager], the [why-this-company] line, the date, your email/phone.\n")

def main():
    cfg = load_config()
    letters = json.load(open(os.path.join(ROOT, "work", "letters.json"), encoding="utf-8"))
    if isinstance(letters, dict):
        letters = letters.get("results", letters.get("letters", []))
    os.makedirs(OUT, exist_ok=True)
    copy_style(cfg.get("resume", {}).get("accent_hex", ""))
    for v in letters:
        for k in ("email_subject", "opening", "closing", "why_company_prompt", "notes_md"):
            v[k] = deent(v.get(k, ""))
        v["body"] = [deent(p) for p in v.get("body", [])]
        folder = os.path.join(OUT, "%s-%s" % (v["id"], v.get("key", v["id"])))
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, "letter.tex"), "w", encoding="utf-8").write(letter_tex(v, cfg))
        open(os.path.join(folder, "letter.md"), "w", encoding="utf-8").write(letter_md(v, cfg))
        print("rendered letter:", folder)
    print("DONE render_coverletters")

if __name__ == "__main__":
    main()
