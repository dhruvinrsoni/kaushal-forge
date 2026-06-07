#!/usr/bin/env python3
"""KaushalForge — one-command orchestrator for the DETERMINISTIC span of the pipeline.

The AI phases P1-P6 (which need a model) are NOT run here — produce work/*.json with the
`kaushal-forge` skill or the prompts/ pack first. This sequencer then runs the deterministic
glue with stage banners, stopping on the first failure:

    intake  ->  render  ->  build  ->  verify  ->  review

    python engine/run.py                         # whole deterministic span (ends at the review checkpoint)
    python engine/run.py --from render --to verify   # just render+build+verify (this is the CI smoke)
    python engine/run.py --from build --to verify --approved   # rebuild only the approved subset
    python engine/run.py --yes                   # non-interactive (CI): no "now go review" pause messaging

Every underlying script stays runnable on its own; this only shells out to them in order."""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PY = sys.executable

def _r(*script_and_args):
    return [PY, os.path.join(HERE, script_and_args[0])] + list(script_and_args[1:])

# ordered deterministic stages -> list of commands to run for that stage
def stage_cmds(name, approved):
    if name == "intake":
        return [_r("intake_dump.py")]
    if name == "render":
        return [_r("render_resumes.py"), _r("render_linkedin.py"),
                _r("render_coverletters.py"), _r("render_strategy.py")]
    if name == "build":
        return [_r("build_pdfs.py", *(["--approved"] if approved else []))]
    if name == "verify":
        return [_r("verify.py")]
    if name == "review":
        return [_r("review.py")]
    return []

STAGES = ["intake", "render", "build", "verify", "review"]

def main():
    args = sys.argv[1:]
    approved = "--approved" in args
    yes = "--yes" in args
    def opt(flag, default):
        return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default
    frm = opt("--from", "render")     # default span skips intake (work/ usually already populated)
    to = opt("--to", "review")
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
        print("\n=== %s ===" % name.upper())
        for cmd in stage_cmds(name, approved):
            label = os.path.basename(cmd[1]) + (" " + " ".join(cmd[2:]) if len(cmd) > 2 else "")
            print("  $ %s" % label)
            rc = subprocess.run(cmd, cwd=ROOT).returncode
            if rc != 0:
                print("\nFAILED at %s (%s exited %d). Fix and re-run with --from %s." % (name, label, rc, name))
                sys.exit(rc)

    print("\nDONE: %s" % " -> ".join(span))
    if "review" in span and not yes:
        print("Review checkpoint: read work/REVIEW.md, flip approve in work/review.yaml, then\n"
              "  python engine/run.py --from build --to verify --approved")
    elif "verify" == span[-1]:
        print("VERIFY passed — toolkit is in output/. Publish with: python engine/publish.py --scan")

if __name__ == "__main__":
    main()
