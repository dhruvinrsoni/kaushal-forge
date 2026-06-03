#!/usr/bin/env python3
"""KaushalForge — consolidate everything in inbox/ into work/00-raw-dump.txt.
Reads .txt/.md/.csv/.json directly; extracts text from .pdf (pypdf) and .docx (python-docx) if available.
Files it can't read are listed with a note to paste their text manually."""
import os, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
INBOX = os.path.join(ROOT, "inbox"); WORK = os.path.join(ROOT, "work")

def read_text(p):
    ext = os.path.splitext(p)[1].lower()
    if ext in (".txt", ".md", ".csv", ".json", ".log", ".tex"):
        return open(p, encoding="utf-8", errors="replace").read()
    if ext == ".pdf":
        try:
            import pypdf
            return "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(p).pages)
        except Exception as e:
            return None
    if ext == ".docx":
        try:
            import docx
            return "\n".join(par.text for par in docx.Document(p).paragraphs)
        except Exception:
            return None
    return None

def main():
    os.makedirs(WORK, exist_ok=True)
    files = [f for f in sorted(glob.glob(os.path.join(INBOX, "**", "*"), recursive=True)) if os.path.isfile(f)]
    out, skipped = [], []
    for f in files:
        if os.path.basename(f) == ".gitkeep": continue
        txt = read_text(f)
        rel = os.path.relpath(f, INBOX)
        if txt is None:
            skipped.append(rel); continue
        out.append(f"\n\n=== FILE: {rel} ===\n{txt}")
    dump = os.path.join(WORK, "00-raw-dump.txt")
    open(dump, "w", encoding="utf-8").write("".join(out))
    print(f"Wrote {dump} from {len(files)-len(skipped)} files ({len(dump)} ...).")
    if skipped:
        print("COULD NOT READ (paste their text into a .txt in inbox/ and re-run):")
        for s in skipped: print("  -", s)
    if not files:
        print("inbox/ is empty. Add the person's data: LinkedIn 'Get a copy of your data' export, "
              "performance reviews, resume, GitHub README, portfolio text, etc.")

if __name__ == "__main__":
    main()
