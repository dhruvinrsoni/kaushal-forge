#!/usr/bin/env python3
"""KaushalForge — consolidate a folder of raw career data into work/00-raw-dump.txt.

Default source is the gitignored inbox/. Pass --data <path> to ingest an EXTERNAL
folder instead, so confidential data never has to be copied into the repo at all.
Reads .txt/.md/.csv/.json directly; extracts text from .pdf (pypdf) and .docx
(python-docx) if available. Files it can't read are listed with a note to paste their
text manually."""
import os, glob, sys, argparse
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
        except Exception:
            return None
    if ext == ".docx":
        try:
            import docx
            return "\n".join(par.text for par in docx.Document(p).paragraphs)
        except Exception:
            return None
    return None

def main(src=INBOX):
    src = os.path.abspath(src)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.isdir(src):
        print(f"ERROR: data folder not found: {src}\n"
              "Pass --data <path> to an existing folder, or put files in inbox/.")
        sys.exit(2)
    files = [f for f in sorted(glob.glob(os.path.join(src, "**", "*"), recursive=True)) if os.path.isfile(f)]
    out, skipped = [], []
    for f in files:
        if os.path.basename(f) == ".gitkeep": continue
        txt = read_text(f)
        rel = os.path.relpath(f, src)
        if txt is None:
            skipped.append(rel); continue
        out.append(f"\n\n=== FILE: {rel} ===\n{txt}")
    dump = os.path.join(WORK, "00-raw-dump.txt")
    open(dump, "w", encoding="utf-8").write("".join(out))
    nread = len(files) - len(skipped)
    print(f"Wrote {dump} from {nread} files (source: {src}).")
    print(f"CONFIRM: this ingested {nread} file(s) for ONE person from {src} — make sure that's the "
          "right person's data before running the AI phases (this becomes their résumés).")
    if skipped:
        print("COULD NOT READ (paste their text into a .txt and re-run):")
        for s in skipped: print("  -", s)
    if not files:
        print(f"{src} is empty. Add the person's data: LinkedIn 'Get a copy of your data' export, "
              "performance reviews, resume, GitHub README, portfolio text, etc.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Consolidate a folder of raw career data into work/00-raw-dump.txt.")
    ap.add_argument("--data", default=INBOX, metavar="PATH",
                    help="Folder of raw career data to ingest (default: inbox/). Point this at any "
                         "external/out-of-tree path so confidential data never enters the repo.")
    main(ap.parse_args().data)
