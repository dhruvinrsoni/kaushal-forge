---
name: systematic-debugging
description: >
  Four-phase debugging protocol with Iron Law — find root cause before any fix.
  Use for any bug, test failure, build failure, or unexpected behavior.
metadata:
  version: "1.0.0"
  dependencies: "constitution"
  reasoning_mode: plan-execute
---

# Systematic Debugging

> "Random fixes waste time and create new bugs. Quick patches mask underlying issues."

---

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If Phase 1 is not complete, no fix may be proposed. This is non-negotiable.

---

## When to Use

Use for **any** technical problem:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance degradation
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (urgency makes guessing tempting)
- "Just a quick fix" seems obvious
- You've already tried multiple fixes that didn't stick
- You don't fully understand the issue

---

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting any fix:**

1. **Read error messages completely** — don't skip stack traces. Note file paths, line numbers, error codes.

2. **Reproduce consistently** — can you trigger it reliably? What are the exact steps? If not reliably reproducible: gather more data, don't guess.

3. **Check recent changes** — `git log --oneline -10`, `git diff HEAD~3`. What changed that could cause this?

4. **Gather evidence in multi-component systems** — add diagnostic instrumentation at each boundary:
   ```bash
   # Before fixing, add logging to see WHERE it breaks
   echo "=== Input at layer 1: $VAR"        # What enters
   echo "=== Output from layer 1: $RESULT"  # What exits
   # Run once to gather evidence → then analyze
   ```

5. **Trace data flow** — where does the bad value originate? Trace backward through the call stack to the source. Fix at source, not at symptom.

### Phase 2: Pattern Analysis

1. **Find working examples** — locate similar code in the codebase that works correctly.

2. **Compare against references** — if implementing a known pattern, read the reference implementation completely. Don't skim.

3. **Identify differences** — list every difference between working and broken, however small. Don't assume "that can't matter."

4. **Understand dependencies** — what config, state, or environment does this code assume?

### Phase 3: Hypothesis and Testing

1. **Form a single hypothesis** — state explicitly: "I think X is the root cause because Y." Write it down.

2. **Test minimally** — make the smallest possible change to test the hypothesis. One variable at a time.

3. **Verify before continuing** — did it work? YES → Phase 4. NO → form a new hypothesis. Do NOT add more fixes on top of failed ones.

4. **When you don't know** — say so. Don't pretend. Research or ask before guessing.

### Phase 4: Implementation

1. **Write a failing test first** — simplest possible reproduction. Automated test if a framework exists.

2. **Implement one fix** — address the root cause identified. No "while I'm here" improvements.

3. **Verify the fix** — test passes? No other tests broken? Issue actually resolved?

4. **If fix doesn't work:**
   - Count: how many fixes have been attempted?
   - If < 3: return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP — question the architecture**

5. **If 3+ fixes failed — question architecture:**
   - Is this pattern fundamentally correct?
   - Are we fixing symptoms of a design problem?
   - Should we redesign vs. continue patching?
   - Discuss before attempting another fix

---

## Red Flags — STOP and Return to Phase 1

If you catch yourself thinking any of these, stop immediately:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes at once, then run tests"
- "It's probably X, let me fix that" (without tracing)
- "I don't fully understand but this might work"
- "Here are the main problems:" (listing fixes before investigation)
- "One more fix attempt" (when 2+ already failed)

---

## Common Rationalizations vs. Reality

| Rationalization | Reality |
|----------------|---------|
| "Issue is simple, no need for process" | Simple bugs have root causes too. Process is fast for simple bugs. |
| "Emergency — no time for process" | Systematic is FASTER than thrashing. Saves 1-2 hours. |
| "Just try this first" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after fix works" | Untested fixes don't stick. Write test first. |
| "Multiple fixes saves time" | Can't isolate what worked. Creates new bugs. |
| "One more attempt" (after 2+ failures) | 3+ failures = wrong architecture. Stop and rethink. |

---

## Quick Reference

| Phase | Key Activity | Done When |
|-------|-------------|-----------|
| 1. Root Cause | Read errors, reproduce, trace data flow | Know WHAT and WHY |
| 2. Pattern | Find working examples, identify differences | Know the gap |
| 3. Hypothesis | Form theory, test minimally | Confirmed root cause |
| 4. Fix | Failing test → one fix → verify | Tests pass, issue gone |

---

## Verification Commands

```bash
# Run tests to verify fix
{{TEST_COMMAND}}

# Check what changed
git diff HEAD~1

# Confirm no regressions
{{BUILD_COMMAND}}
```
