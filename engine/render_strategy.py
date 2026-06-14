#!/usr/bin/env python3
"""KaushalForge — copy work/strategy/*.md -> output/Strategy/ and write an index."""
import os, sys, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # engine/ (for kf_lib)
from kf_lib import AI_DISCLAIMER_MD
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "work", "strategy"); OUT = os.path.join(ROOT, "output", "Strategy")

def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "*.md")))
    for f in files:
        shutil.copy2(f, os.path.join(OUT, os.path.basename(f)))
    idx = AI_DISCLAIMER_MD + "\n# Strategy\n\n" + "\n".join(f"- [{os.path.basename(f)[:-3]}]({os.path.basename(f)})" for f in files) + "\n"
    open(os.path.join(OUT, "00-index.md"), "w", encoding="utf-8").write(idx)
    print("DONE render_strategy:", len(files), "docs")

if __name__ == "__main__":
    main()
