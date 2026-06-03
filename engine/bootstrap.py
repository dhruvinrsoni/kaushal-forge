#!/usr/bin/env python3
"""KaushalForge — one-time setup: install Python deps + resolve/download Tectonic (LaTeX engine).
Writes the resolved tectonic path to engine/.tectonic_path so the other scripts find it.
Fallback: if download fails, you can still compile every build-*.tex on Overleaf."""
import os, sys, subprocess, shutil, platform, zipfile, tarfile, json, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, ".bin")
PATHFILE = os.path.join(HERE, ".tectonic_path")

def pip_install():
    for pkg in ("pypdf", "pyyaml"):
        try:
            __import__("yaml" if pkg == "pyyaml" else pkg)
        except ImportError:
            print("installing", pkg)
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", pkg])

def existing_tectonic():
    for c in (os.environ.get("CAREERFORGE_TECTONIC"), shutil.which("tectonic"),
              os.path.join(BIN, "tectonic.exe"), os.path.join(BIN, "tectonic"),
              os.path.expanduser(r"~\AppData\Local\tectonic\tectonic.exe")):
        if c and os.path.exists(c):
            return c
    return None

def asset_filter():
    sysname = platform.system().lower()
    if sysname == "windows": return lambda n: n.endswith("x86_64-pc-windows-msvc.zip")
    if sysname == "darwin":  return lambda n: "apple-darwin" in n and n.endswith(".tar.gz")
    return lambda n: "linux" in n and n.endswith(".tar.gz")  # gnu linux

def download_tectonic():
    os.makedirs(BIN, exist_ok=True)
    req = urllib.request.Request("https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest",
                                 headers={"User-Agent": "kaushal-forge"})
    rel = json.load(urllib.request.urlopen(req))
    match = asset_filter()
    asset = next((a for a in rel["assets"] if match(a["name"])), None)
    if not asset:
        raise RuntimeError("no Tectonic asset for this platform; install manually or use Overleaf.")
    dest = os.path.join(BIN, asset["name"])
    print("downloading", asset["name"])
    urllib.request.urlretrieve(asset["browser_download_url"], dest)
    if dest.endswith(".zip"):
        with zipfile.ZipFile(dest) as z: z.extractall(BIN)
    else:
        with tarfile.open(dest) as t: t.extractall(BIN)
    for root, _, files in os.walk(BIN):
        for f in files:
            if f in ("tectonic", "tectonic.exe"):
                return os.path.join(root, f)
    raise RuntimeError("tectonic binary not found after extraction")

def main():
    pip_install()
    tec = existing_tectonic()
    if not tec:
        try:
            tec = download_tectonic()
        except Exception as e:
            print("WARN: could not auto-install Tectonic:", e)
            print("      Install MiKTeX/TeX Live/Tectonic manually, or compile build-*.tex on Overleaf.")
            return
    open(PATHFILE, "w", encoding="utf-8").write(tec)
    print("Tectonic:", tec)
    print("Wrote", PATHFILE)
    print("Setup OK. Next: fill config.yaml, drop data in inbox/, run intake_dump.py, then the AI phases.")

if __name__ == "__main__":
    main()
