---
name: repo-maintenance
description: >
  Adaptive cleanup framework with greedy optimization. Starts with a simple goal,
  discovers value through exploration, pivots strategy toward maximum impact.
  "A manager who wastes nothing."
metadata:
  version: "2.0.0"
  dependencies: "constitution"
  reasoning_mode: plan-execute
---

# Repo Maintenance — Adaptive Value Optimization v2.0

> "A manager who wastes nothing. Start simple, discover value, pivot toward greater good."

---

## Philosophy: The Greedy Pivot

Traditional cleanup says: "Fewer files = better." This skill says: **"Maximum value per file = better."**

Start with a simple heuristic (fewer files). As you explore, discover what's truly unique. Pivot your strategy when exploration reveals higher-value outcomes than your starting assumption.

The key insight: **at each decision point, ask "Is this content available somewhere better?"**
- **YES** → merge unique parts upstream, then delete the duplicate
- **NO** → trim it to essentials and keep it

---

## Phase 0: Reconnaissance (Read-Only — Touch Nothing)

Before making any changes, build a complete inventory:

```bash
# 1. All tracked files with sizes
git ls-files | while read f; do echo "$(wc -c < "$f") $f"; done | sort -rn

# 2. Recent activity for context
git log --oneline -20

# 3. What changed recently (active vs dormant signal)
git log --diff-filter=M --name-only --since="3 months ago" --pretty=format: | sort -u

# 4. Files NOT modified in 6+ months (dormant candidates)
git log --diff-filter=M --name-only --since="6 months ago" --pretty=format: | sort -u > /tmp/recent.txt
git ls-files | sort > /tmp/all.txt
comm -23 /tmp/all.txt /tmp/recent.txt

# 5. Dependency freshness (if applicable)
npm outdated 2>/dev/null || pip list --outdated 2>/dev/null || ./gradlew dependencyUpdates 2>/dev/null
```

**Output:** Categorize every file into: `{ active, dormant, stale, unknown }`

| Category | Definition | Next Step |
|----------|-----------|-----------|
| Active | Modified in last 3 months or referenced in configs | Skip — do not touch |
| Dormant | Not modified in 6+ months but has references | Evaluate with 4 Questions |
| Stale | No references found anywhere | Evaluate with 4 Questions |
| Unknown | Can't determine status from automated checks | Manual review |

---

## Phase 1: Value Assessment — The 4 Questions

For each file in `{ dormant, stale, unknown }`, ask **in order** (stop at first YES):

| # | Question | How to check | If YES |
|---|----------|-------------|--------|
| 1 | **Referenced anywhere?** | `grep -r "filename" src/ .github/ *.json *.yml *.md` | **KEEP** — do not touch |
| 2 | **Has unique value not covered elsewhere?** | Compare against similar files line-by-line | **MERGE** unique parts → then remove |
| 3 | **Can be activated with minimal effort?** | Check for missing config entries (package.json scripts, workflow refs) | **ACTIVATE** — wire it up |
| 4 | **Represents irreplaceable human effort?** | Check git blame age + complexity + creative content | **ARCHIVE** to `legacy/` |
| — | All four are NO | — | **DELETE** |

### Decision Matrix with Examples

| File | Q1 Referenced? | Q2 Unique? | Q3 Activatable? | Q4 Irreplaceable? | Action |
|------|---------------|-----------|----------------|-------------------|--------|
| `scripts/benchmark.mjs` | No | Yes (KB thresholds) | Yes (add to package.json) | — | **ACTIVATE** |
| `src/assets/v1-icon.svg` | No | No (superseded) | No | Yes (AI prompt effort) | **ARCHIVE** |
| `old-webpack.config.js` | No | No (esbuild replaced) | No | No | **DELETE** |
| `docs/ALGORITHM.md` | No | Yes (public narrative) | — | — | **KEEP** (trim) |

---

## Phase 2: Adaptive Strategy — The Checkpoint Rule

**After every 5 decisions, STOP and reassess:**

### Checkpoint Questions

1. "Has exploration revealed a **higher-value goal** than my starting assumption?"
2. "Am I **destroying unique content** that exists nowhere else?"
3. "Would the repo be **better with this file trimmed and kept** than with it gone?"
4. "Has my understanding of the repo **changed** since I started?"

### Strategy Evolution Log

Track how your strategy evolves. Example:

```
Decision 1-5:   Strategy = "fewer files" → deleted 3 truly dead files
Decision 6-10:  PIVOT → found docs with unique branding narrative
                Strategy = "maximize value per file" → trimmed 2 docs, kept both
Decision 11-15: PIVOT → found dormant scripts that work perfectly
                Strategy = "activate > delete" → wired up 2 scripts to package.json
Decision 16+:   Strategy stabilized → cleanup remaining dead code
```

### Documented Pivot Patterns

| Started with | What exploration revealed | Pivoted to |
|-------------|--------------------------|------------|
| "Delete unused docs" | Doc has unique branding narrative not in CLAUDE.md | Trim to essentials, keep |
| "Remove old icons" | Icons represent hours of AI prompt iteration | Archive to `legacy/`, don't delete |
| "Fewer scripts" | Script works but missing package.json entry | Activate — add the entry |
| "Simplify configs" | Old config documents a migration decision | Keep as ADR reference |
| "Delete test fixtures" | Fixtures encode edge cases not in unit tests | Convert to test cases, then delete fixtures |
| "Remove changelogs" | Changelog has etymology and algorithm philosophy | Recover, trim verbose sections, keep core |

### The "Best from Waste" Rule

Before deleting anything with >50 lines, ask:
- Can I extract a **useful snippet** into an existing file?
- Can I convert this into a **test case** or **documentation**?
- Can I **activate** this with a one-line config change?
- Does this represent **creative work** that can't be regenerated cheaply?

If any answer is YES → extract value first, then decide.

---

## Phase 3: Execution

### Commit Grouping by Intent

Group changes by **what they achieve**, not by file location:

```bash
# Group 1: Remove confirmed dead code
git add <dead-files>
git commit -m "chore: remove dead code — unreferenced, fully superseded"

# Group 2: Archive historical artifacts
git mv src/assets/v1-icons/ src/assets/legacy/
git commit -m "chore: archive legacy icon history to legacy/"

# Group 3: Activate dormant tools
# (edit package.json to add script entries, then)
git add package.json scripts/benchmark.mjs
git commit -m "chore: activate dormant benchmark script"

# Group 4: Trim verbose docs
git add docs/ALGORITHM.md
git commit -m "docs: trim algorithm doc — remove verbose AI deep-dives, keep core narrative"

# Group 5: Merge duplicates
git add src/utils/merged-helper.ts
git rm src/utils/old-helper.ts
git commit -m "refactor: merge old-helper into merged-helper, remove duplicate"
```

**Rules:**
- Use `git mv` (not `rm` + `add`) for archives — preserves `git log --follow`
- Never commit deletions and additions in the same commit — makes reverting easier
- Each commit message explains the **why** (e.g., "unreferenced, fully superseded")

---

## Phase 4: Verification

After cleanup, verify nothing broke:

```bash
# 1. Build passes
{{BUILD_COMMAND}}

# 2. Tests pass
{{TEST_COMMAND}}

# 3. No broken imports (search for deleted/moved filenames)
for f in $(git diff --name-only --diff-filter=D HEAD~5); do
  basename="$(basename "$f" | sed 's/\.[^.]*$//')"
  grep -rn "$basename" src/ .github/ --include="*.ts" --include="*.js" --include="*.yml" --include="*.json" && echo "WARNING: $f still referenced"
done

# 4. No broken workflow references
for f in $(git diff --name-only --diff-filter=D HEAD~5); do
  grep -rn "$(basename "$f")" .github/workflows/ && echo "WARNING: workflow references deleted file $f"
done

# 5. Summary — confirm net reduction in noise, not value
echo "Files before: $(git diff --stat HEAD~5 | tail -1)"
echo "Total tracked: $(git ls-files | wc -l)"
```

### Success Criteria

- Build and tests pass
- Zero broken imports or workflow references
- File count reduced OR value-per-file increased (not both required)
- No unique content lost (verified by checkpoint reviews)
- Every deletion has a documented justification in commit messages

---

## Anti-Patterns — Red Flags to Watch For

If you catch yourself thinking any of these, **STOP and return to Phase 1**:

1. "I'll just delete everything that looks old" → **No.** Check references first.
2. "This file name is similar to another, so it's a duplicate" → **No.** Compare logic line-by-line.
3. "Nobody uses this" → **No.** Grep the entire repo including configs, workflows, and docs.
4. "It's just a doc, I can regenerate it" → **No.** Check if it contains creative/narrative content.
5. "The README covers this" → **No.** README is public-facing; SKILL.md is developer-facing. Different audiences.
6. "I'll clean up the whole thing in one commit" → **No.** Group by intent.
7. "This config is for a tool we don't use" → **Verify.** Check package.json, workflows, and scripts first.
8. "Fewer files is always better" → **No.** One well-trimmed file > zero files when content is unique.

---

## Quick Reference: Cleanup Audit Commands

```bash
# Find all tracked files sorted by size
git ls-files | xargs wc -c 2>/dev/null | sort -rn | head -30

# Find imports/references for a suspicious file
grep -r "suspect-filename" src/ .github/ --include="*.ts" --include="*.js" --include="*.yml" --include="*.json"

# Check if a script is wired up
grep "script-name" package.json pyproject.toml Makefile 2>/dev/null

# Check if an asset is referenced
grep -r "asset-name" . --include="*.html" --include="*.json" --include="*.yml" --include="*.md"

# Files not touched in 6 months
git log --diff-filter=M --name-only --since="6 months ago" --pretty=format: | sort -u > /tmp/recent.txt
git ls-files | sort > /tmp/all.txt
comm -23 /tmp/all.txt /tmp/recent.txt

# Who last touched a file and when
git log -1 --format="%ai %an" -- <file>
```
