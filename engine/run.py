#!/usr/bin/env python3
"""KaushalForge — one-command orchestrator for the DETERMINISTIC span of the pipeline.

The AI phases P1-P6 (which need a model) are NOT run here — produce work/*.json with the
`kaushal-forge` skill or the prompts/ pack first. This sequencer then runs the deterministic
glue with stage banners, stopping on the first failure:

    intake  ->  render  ->  review  ->  build  ->  verify

Review comes BEFORE build on purpose: a human reads work/REVIEW.md and sets `reviewed: 1`
in work/review.yaml; the approved build + publishing refuse until then. In an interactive
terminal this script also PAUSES before build for an explicit y/N.

    python engine/run.py                              # render -> review -> (pause) -> build -> verify
    python engine/run.py --from build --to verify --approved   # build only the approved subset
    python engine/run.py --from render --to verify --yes        # non-interactive (CI): no pause, no gate

Every underlying script stays runnable on its own; this only shells out to them in order."""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PY = sys.executable

def _r(*script_and_args):
    return [PY, os.path.join(HERE, script_and_args[0])] + list(script_and_args[1:])

# ordered deterministic stages -> list of commands to run for that stage
def stage_cmds(name, approved, yes):
    if name == "intake":
        return [_r("intake_dump.py")]
    if name == "render":
        return [_r("render_resumes.py"), _r("render_linkedin.py"),
                _r("render_coverletters.py"), _r("render_strategy.py")]
    if name == "review":
        return [_r("review.py")]
    if name == "build":
        extra = (["--approved"] if approved else []) + (["--yes"] if yes else [])
        return [_r("build_pdfs.py", *extra)]
    if name == "verify":
        return [_r("verify.py")]
    return []

STAGES = ["intake", "render", "review", "build", "verify"]

def confirm_build(yes):
    """Force a human OK before the build (the artifacts that represent a real person)."""
    if yes:
        return
    msg = ("\nCHECKPOINT before BUILD: read work/REVIEW.md, fix any work/*.json, and set "
           "`reviewed: 1` in work/review.yaml for the approved build.")
    if not sys.stdin.isatty():
        print(msg)
        print("Refusing to BUILD non-interactively without --yes (no human to confirm). "
              "Re-run with --yes for automation.")
        sys.exit(1)
    print(msg)
    ans = input("Continue to BUILD now? [y/N] ").strip().lower()
    if ans not in ("y", "yes"):
        print("Stopped before BUILD. Nothing was built. Re-run when you're ready.")
        sys.exit(0)

def main():
    args = sys.argv[1:]
    approved = "--approved" in args
    yes = "--yes" in args
    def opt(flag, default):
        return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default
    frm = opt("--from", "render")     # default span skips intake (work/ usually already populated)
    to = opt("--to", "verify")
    for n in (frm, to):
        if n not in STAGES:
            print("unknown stage '%s'. choose from: %s" % (n, ", ".join(STAGES))); sys.exit(2)
    span = STAGES[STAGES.index(frm):STAGES.index(to) + 1]

    # friendly guard: render needs the AI's output present
    if "render" in span and not os.path.exists(os.path.join(ROOT, "work", "variants.json")):
        print("ERROR: work/variants.json not found. Run the AI phases P1-P6 first "
              "(invoke the kaushal-forge skill, or use prompts/), then re-run this.")
        sys.exit(2)

    print("KaushalForge run: %s  (%s%s)" % (" -> ".join(span),
          "approved-only" if approved else "all", ", non-interactive" if yes else ""))
    for name in span:
        if name == "build":
            confirm_build(yes)
        print("\n=== %s ===" % name.upper())
        for cmd in stage_cmds(name, approved, yes):
            label = os.path.basename(cmd[1]) + (" " + " ".join(cmd[2:]) if len(cmd) > 2 else "")
            print("  $ %s" % label)
            rc = subprocess.run(cmd, cwd=ROOT).returncode
            if rc != 0:
                print("\nFAILED at %s (%s exited %d). Fix and re-run with --from %s." % (name, label, rc, name))
                sys.exit(rc)

    print("\nDONE: %s" % " -> ".join(span))
    if "verify" == span[-1]:
        print("VERIFY passed — toolkit is in output/. To publish (requires reviewed: 1): "
              "python engine/publish.py --scan")

if __name__ == "__main__":
    main()
