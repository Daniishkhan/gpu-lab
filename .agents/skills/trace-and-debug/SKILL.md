---
name: trace-and-debug
description: Loop-by-loop Socratic debugging for local CPU exercises in Antigravity IDE — runs pytest first, builds small-input iteration traces, guides F5 breakpoint placement with inline values, and gives progressive hints without spoiling solutions.
---

# Loop-by-Loop Trace & Debug (`gpu/lab`)

Use this skill whenever the learner is stuck on a local CPU exercise in `exercises/<NN>-<slug>/<mod>.py`, hits a failing `pytest` test, or asks to trace a loop iteration by iteration inside **Antigravity IDE**.

## Non-Negotiable Rules

1. **Run `pytest` first — never guess:** Execute the exact failing test with local variables shown:
   ```bash
   .venv/bin/python -m pytest -k "<test_or_module>" -vv --tb=short -l
   ```
2. **Never give away the solution:** Never write drop-in function bodies, complete formulas, or copy-pasteable fixes in chat or in `exercises/`. Guide the learner so their own hands write the fix.
3. **One step per turn:** Do not dump a 5-step answer at once. Give one focused trace or hint, ask a concrete prediction question, and wait for the learner's response.
4. **Stay inside `curriculum.json` `requires`:** Only use Python/NumPy concepts introduced up to this topic's stage.

## 4-Step Loop-Tracing Ladder (Escalate One Rung Per Turn)

### Rung 1: Tiny Hand-Trace Table (2–4 Elements)
Take the smallest failing test input (or shrink it to 2–4 elements) and show a crisp iteration-by-iteration table comparing **what the learner's code actually did** vs. **what the contract expects**:

| Step | Loop var (`i`, `x`) | State before line | State after line | Notice |
|---|---|---|---|---|
| 0 | ... | ... | ... | ... |

Point to the **exact iteration** where actual state diverges from expected state — without writing the fixed line.

### Rung 2: Antigravity IDE Breakpoint & Watch Guide
Because the workspace enables `"debug.inlineValues": "on"` and `justMyCode: true` in `.vscode/settings.json` + `.vscode/launch.json`, tell the learner:
1. **Exact file & line number** in `exercises/<NN>-<slug>/<mod>.py` to drop a red breakpoint.
2. **Which launch config to run:** press **`F5`** (*Debug Current Exercise (pytest)* works from either `<mod>.py` or `test_<mod>.py`, or *Debug Specific Test (Prompt)* for a single test name).
3. **2–3 specific variables / expressions to watch** as they press **`F10`** (Step Over) across two loop iterations (e.g., `len(out)`, `i`, `grid[r][c]`).

If the test setup has extra noise, optionally offer a 5-line standalone driver inside the gitignored `scratch/` folder (run with `F5` → *Debug Current Python File (Loop Trace)*) — never put scratch prints or drivers inside `exercises/`.

### Rung 3: Contract, Boundary & Aliasing Check
Focus on the single missing invariant:
- Boundary condition (`range` stop off-by-one, empty input, negative input, `<= 0` guard raising `ValueError`).
- Aliasing / mutation (`b = a` mutating caller's list, default mutable arg, shallow `[[0]*n]*m` grid).
- Units or shape mismatch (`1e9` vs `1024**3`, `(B, T, D_in)` vs `(D_in, D_out)`, `axis=0` vs `axis=1`).

### Rung 4: Narrow Structural Hint
Describe the missing step in plain English (one sentence), referencing the exact concept in the linked chapter (`book/sections/<NN>-<slug>/concepts/*.html`) or `book/python-cheatsheet.html`, and let the learner type the code and save (`Cmd+S` auto-runs `pytest` in the Study Cockpit).
